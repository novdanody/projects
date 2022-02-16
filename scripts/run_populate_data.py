import argparse
from data.nasdaqdatahandler import NasdaqDataHandler
from utils.logger import logger


def main(tag, source):
    if source == "nasdaq":
        handler = NasdaqDataHandler(tag)
        # data = handler.obtain()
        data = handler.get()
        logger.info("Data has %d columns", len(data))
    else:
        raise ValueError("Undefined Data Source")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Collect data from specified data source")
    parser.add_argument('--source',
                        help='which data source to collect from',
                        choices=['nasdaq'],
                        default='nasdaq')
    parser.add_argument('--tag',
                        help='what data to collect',
                        choices=['CHRIS/ICE_KC1', 'ODA/PCOFFOTM_USD'],
                        default='CHRIS/ICE_KC1')
    args = parser.parse_args()
    logger.info("Collecting data %s from source %s", args.tag, args.source)
    main(args.tag, args.source)
    # exit(0)
