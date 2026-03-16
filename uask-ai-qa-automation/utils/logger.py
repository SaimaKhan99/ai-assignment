"""Logging helpers for the framework."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from utils.config import LOG_FILE_PATH


LOG_FORMAT = "%(asctime)s | %(levelname)s | %(filename)s | %(message)s"


def get_logger(name: str = "uask_qa") -> logging.Logger:
    """Return a configured logger instance."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    logger.propagate = False

    file_handler = RotatingFileHandler(
        LOG_FILE_PATH,
        maxBytes=2_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(LOG_FORMAT))

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger
