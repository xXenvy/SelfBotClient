from logging import DEBUG, StreamHandler, getLogger, Logger
from colorlog import ColoredFormatter


class Logger:
    __slots__ = ("logger", "_status")

    log_level: int = DEBUG
    log_format: str = "%(log_color)s%(levelname)s | %(asctime)s > %(message)s"

    def __init__(self):
        """
        The __init__ function is called when the class is instantiated.
        It sets up the logger with a colored formatter and stream handler,
        and then adds that handler to the logger. It also sets up a status variable.

        :param self: Represent the instance of the class
        :return: The logger, which is an instance of the logger class
        """

        formatter = ColoredFormatter(self.log_format, datefmt='%H:%M:%S')
        stream = StreamHandler()
        stream.setLevel(self.log_level)
        stream.setFormatter(formatter)

        self.logger = getLogger('Logger')
        self.logger.setLevel(self.log_level)
        self.logger.addHandler(stream)
        self.logger._status = True
