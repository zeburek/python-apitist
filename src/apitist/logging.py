import logging
import sys

import apitist

LOG_LEVEL = logging.INFO


def setup_logging(log_level):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    fmt = "[%(asctime)s][%(levelname)s][%(name)s]: %(message)s"
    date_fmt = "%Y-%m-%d %H:%M:%S"
    logging.basicConfig(
        level=log_level, stream=sys.stdout, format=fmt, datefmt=date_fmt
    )
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

    logger = logging.getLogger(apitist.dist_name)
    logger.setLevel(log_level)
    return logger


_logger = setup_logging(LOG_LEVEL)
