import logging
import sys

import apitist


class Logging:

    LOG_LEVEL = logging.INFO
    logger = None

    @staticmethod
    def set_logging_level(value):
        Logging.LOG_LEVEL = value
        Logging._setup_logging(Logging.LOG_LEVEL)

    @staticmethod
    def _setup_logging(log_level):
        """Setup basic logging

        Args:
          log_level (int): minimum loglevel for emitting messages
        """
        fmt = "[%(asctime)s][%(levelname)s][%(name)s]: %(message)s"
        date_fmt = "%Y-%m-%d %H:%M:%S"
        color_fmt = "%(log_color)s{}%(reset)s".format(fmt)

        # Suppress overly verbose logs from libraries that aren't helpful
        if log_level == logging.DEBUG:
            logging.getLogger("requests").setLevel(logging.DEBUG)
            logging.getLogger("urllib3").setLevel(logging.DEBUG)
        else:
            logging.getLogger("requests").setLevel(logging.WARNING)
            logging.getLogger("urllib3").setLevel(logging.WARNING)

        try:
            from colorlog import ColoredFormatter

            logging.getLogger().handlers[0].setFormatter(
                ColoredFormatter(
                    color_fmt,
                    datefmt=date_fmt,
                    reset=True,
                    log_colors={
                        "DEBUG": "cyan",
                        "INFO": "green",
                        "WARNING": "yellow",
                        "ERROR": "red",
                        "CRITICAL": "red",
                    },
                )
            )
        except ImportError:
            pass
        fmt_ = logging.Formatter(fmt=fmt, datefmt=date_fmt)
        stm = logging.StreamHandler()
        stm.setFormatter(fmt_)
        Logging.logger = logging.getLogger(apitist.dist_name)
        Logging.logger.addHandler(stm)
        Logging.logger.setLevel(log_level)


Logging._setup_logging(Logging.LOG_LEVEL)
