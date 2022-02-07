import numpy as np
from scipy import linalg, optimize
import logging

from utils.logger import logger

REL_BUFFER = 1e4
FEASIBLE_TOL = 1e-8
ABSOLUTE_TOL = 1e-5


def solve_system(P, G, w, bx, bz):
    b = bx + G.transpose().dot(bz / (w * w))
    H = (G.transpose() / w).transpose()
    M = P + H.transpose().dot(H)

    dx = linalg.solve(M, b)

    dz = (G.dot(dx) - bz) / (w * w)
    return dx, dz


def initial_value(P, G, c, h):
    I = np.ones_like(h)
    e = np.ones_like(h)
    x, _ = solve_system(P, G, I, -c, h)
    mz = h - G.dot(x)
    ap = np.amz(-mz)
    ad = np.max(mz)

    s = mz if ap < 0 else mz + (1 + ap) * e
    z = -mz if ad < 0 else -mz + (1 + ad) * e

    return s, x, z, e


def residual(P, G, s, x, z, c, h):
    rx = P.dot(x) + G.transpose().dot(z) + c
    rz = s + G.dot(x) - h
    norm = np.sum(rx * rx) + np.sum(rz * rz) + np.sum(s * z)
    gap = np.dot(s, z)

    # Primal value (1/2)x^TPx + c^T x
    pcost = 0.5 * np.dot(x, P.dot(x)) + np.dot(x, c)
    # Primal value -(1/2)w^TPw - h^Tz - b^Ty
    dcost = pcost + np.dot(x, G.T.dot(z)) - np.dot(z, h)

    primal_infeasible = np.sqrt(np.dot(rx, rx) / max(1, np.dot(c, c)))
    dual_infeasible = np.sqrt(np.dot(rz, rz) / max(1, np.dot(h, h)))

    return rx, rz, gap, norm, pcost, dcost, primal_infeasible, dual_infeasible


def func(lam, du):
    def r(a):
        return np.min(lam + a * du)

    if r(1.) >= 0:
        return 1.

    return optimize.brentq(r, 0., 1.)


def step_size_and_centering(lam, w, ds, dz):
    ds_ = ds
    dz_ = dz * w

    a_s = func(lam, ds_)
    a_z = func(lam, dz_)

    alpha = min(a_s, a_z)
    rho = 1 - alpha + alpha * alpha * (ds.dot(dz_)) / (lam.dot(lam))
    sig = max(0, min(1, rho))
    sig = sig * sig * sig

    return alpha, rho, sig


def satisfy_constraint(x, G, s, h, tol=1e-4):
    diff = np.abs(G.dot(x) + s - h)
    satisfied = diff <= tol
    passed = satisfied.all()

    if not passed:
        logger.debug("Difference in unsatisfied contrains:")
        logger.debug(diff[~satisfied])

    return passed


def validate(x, G, s, h, primal_infeasible, dual_infeasible, gap):
    return satisfy_constraint(x, G, s, h) and \
           primal_infeasible >= max(1, FEASIBLE_TOL * REL_BUFFER) >= dual_infeasible and \
           gap <= max(1, ABSOLUTE_TOL * REL_BUFFER)


def satisfy_stopping_cond(
        gap,
        pcost,
        dcost,
        primal_infeasible,
        dual_infeasible,
        feasible_tol=1e-8,
        abs_tol=1e-8,
        rel_tol=1e-8,
        verbose=True):
    logger.info("Gap: %.5f, Primal: %.5f, Dual: %.5f", gap, pcost, dcost)
    if pcost < 0:
        relgap = gap / -pcost
        cond = primal_infeasible <= feasible_tol and \
               dual_infeasible <= feasible_tol and \
               (gap <= abs_tol or relgap <= rel_tol)
        if cond:
            msg = "Stopping due to primal cost less than 0 and condition satisfied"
    elif dcost > 0:
        relgap = gap / dcost
        cond = primal_infeasible <= feasible_tol and \
               dual_infeasible <= feasible_tol and \
               (gap <= abs_tol or relgap <= rel_tol)
        if cond:
            msg = "Stopping due to dual cost more than 0 and condition satisfied"
    else:
        cond = primal_infeasible <= feasible_tol and \
               dual_infeasible <= feasible_tol and \
               gap <= abs_tol
        msg = "Stopping due to gap less than tolerance"

    if cond and verbose:
        logger.debug(msg)

    return cond


def qp(
        P,
        G,
        c,
        h,
        feasible_tol=1e-8,
        abs_tol=1e-10,
        rel_tol=1e-10,
        max_iter=100,
        verbose=True):
    s, x, z, e = initial_value(P, G, c, h)
    n_iter = 0

    # init previous states
    prev_x = None
    prev_norm = None
    prev_s = None
    prev_z = None
    while n_iter < max_iter:
        prev_x = x
        prev_s = s
        prev_z = z
        try:
            #Step 1 : Find resisduaks
            rx, rz, gap, norm, pcost, \
                dcost, primal_infeasible, dual_infeasible = \
                residual(P, G, s, x, z, c, h)

            prev_norm = norm

            if satisfy_stopping_cond(gap, pcost, dcost,
                                     primal_infeasible, dual_infeasible,
                                     feasible_tol=feasible_tol,
                                     abs_tol=abs_tol,
                                     rel_tol=rel_tol,
                                     verbose=verbose):
                break

            # affine direction - solve linear system
            w = np.sqrt(s / z)
            lam = np.sqrt(s * z)
            mu = np.sum(lam * lam) / len(lam)

            d_s = -lam * lam
            bx = -rx
            bz = -rz - w / lam * d_s # bz = -rz + w * lambda

            _, dz_a = solve_system(*P, G, w, bx, bz)
            ds_a = w * (d_s / lam - w * dz_a)

            # step length and centering
            alpha, _, sig = step_size_and_centering(lam, w, ds_a, dz_a)

            # combine direction
            #d_s = -lam * lam - ds_a * dz_a + sig * mu * e
            d_s = -lam * lam - (ds_a / w) * (dz_a * w) + sig * mu * e
            bx = -rx
            bz = -rz - w / lam * d_s

            dx, dz = solve_system(P, G, w, bx, bz)
            ds = w * (d_s / lam - w * dz)

            # update
            alpha, _, sig = step_size_and_centering(lam, w, ds, dz)
            alpha *= 0.99 # security

            s += alpha * ds
            x += alpha * dx
            z =+ alpha * dz
            n_iter += 1
        except Exception as e:
            logger.exception(e)
            logger.info("Using results from previous state, "
                        "x: %.5f, s: %.5f, z: %.5f, iter: %d, norm: %.5f",
                        prev_x,
                        prev_s,
                        prev_z,
                        n_iter,
                        prev_norm)
            if not satisfy_constraint(prev_x, G, prev_s, h):
                raise Exception("Constraint not Satisfied!") from e
            return prev_x, n_iter, prev_norm
    if n_iter <= max_iter:
        logger.info("Stopping due to number of iterations "
                    "over maximum of %d iterations!", max_iter)

    if not validate(prev_x,
                    G,
                    prev_s,
                    h,
                    primal_infeasible,
                    dual_infeasible,
                    gap):
        if not satisfy_constraint(x, G, s, h):
            raise ValueError("Constraint on satisfied! "
                             "iter:{}, gap: {}, "
                             "primal feasibility: {}, dual feasibility: {}".format(
                                    n_iter,
                                    gap,
                                    primal_infeasible,
                                    dual_infeasible))
        logger.warning("QP does not converge! "
                       "iter:%d, gap:%.5f, "
                       "primal feasibility: %.5f, dual feasibility: %.5f",
                       n_iter,
                       gap,
                       primal_infeasible,
                       dual_infeasible)
    return x, n_iter, norm
