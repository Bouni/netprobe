# Logging helper
#
# - Sets up logging config

import logging
from logging.handlers import RotatingFileHandler


def setup_logging(config):
    # Logging config
    logger = logging.getLogger("logs")
    logger.setLevel(logging.DEBUG)

    # Prevent adding handlers multiple times
    if logger.hasHandlers():
        return logger  # If handlers already exist, return the logger as is

    # Set formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(filename)s %(funcName)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if "logfile" in config:
        # File handler (rotating logs)
        fileHandler = RotatingFileHandler(
            filename=config.logfile.filename, maxBytes=5_000_000, backupCount=3
        )
        fileHandler.setFormatter(formatter)
        fileHandler.setLevel(level=config.logfile.level)
        logger.addHandler(fileHandler)

    # Console handler (stdout)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(config.console.level)

    logger.addHandler(console_handler)

    return logger
