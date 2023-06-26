from logging import DEBUG, StreamHandler, getLogger
from colorlog import ColoredFormatter


class Logger:
    """
    It sets up the logger with a colored formatter and stream handler,
    and then adds that handler to the logger. It also sets up a status variable.
    """

    __slots__ = ("logger", "_status", "debug", "error", "warning")

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
        self.logger._status = True  # pyright: ignore
