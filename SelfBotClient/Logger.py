from logging import DEBUG, StreamHandler, getLogger, Logger
from colorlog import ColoredFormatter


class Logger:
    __slots__ = ("logger",)

    log_level: int = DEBUG
    log_format: str = "%(log_color)s%(levelname)s | %(asctime)s > %(message)s"

    def __init__(self):
        formatter = ColoredFormatter(self.log_format, datefmt='%H:%M:%S')
        stream = StreamHandler()
        stream.setLevel(self.log_level)
        stream.setFormatter(formatter)

        self.logger = getLogger('Logger')
        self.logger.setLevel(self.log_level)
        self.logger.addHandler(stream)
