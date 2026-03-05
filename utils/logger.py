"""Logging helper module."""
import logging
from logging.handlers import RotatingFileHandler


def configure_logger(name: str, log_path: str = "blindnav.log") -> logging.Logger:
    """Return a configured rotating logger."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    )

    file_handler = RotatingFileHandler(log_path, maxBytes=1_000_000, backupCount=2)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger
