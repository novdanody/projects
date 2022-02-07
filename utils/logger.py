import os
import re
import logging
import threading

logger = logging.getLogger()
logger.setLevel("logging.DEBUG")
logFormatter = logging.Formatter(
    "%(asctime)s [%(levelname)-5.5s] [%(processName)s] %(message)s")

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
DEFAULT_FLOAT = '{:,.2f}'.format


def log_df(data, level=logging.debug, float_format=DEFAULT_FLOAT):
    as_str = data.to_string(float_format=float_format)
    tokens = as_str.split('\n')
    for token in tokens:
        logger.log(level, "%s", token)


def clean_str(source):
    pattern_replacements = {
        r"[\r\n]": "",
        r"[\t\s]+": " "
    }
    dest = source
    for pattern, replacement in pattern_replacements.items():
        dest = re.sub(pattern , replacement, dest)

    return dest.strip()


class LogPipe(threading.Thread):
    def __init__(self, level):
        """
        Setup the object with a logger and a loglevel and start thread"
        """
        threading.Thread.__init__(self)
        self.daemon = False
        self.level = level
        self.fd_read, self.fd_write = os.pipe()
        self.pipe_reader = os.fdopen(self.fd_read)
        self.start()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def fileno(self):
        """
        Return write file descriptor of the pipe
        """
        return self.fd_write

    def run(self):
        """
        Run the thread, logging everything
        """
        for line in iter(self.pipe_reader.readline, ''):
            logger.log(self.level, line.strip('\n'))

        self.pipe_reader.close()

    def close(self):
        """
        Close the write end of the pipe
        """
        os.close(self.fd_write)