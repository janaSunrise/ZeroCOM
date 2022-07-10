from __future__ import annotations

import logging
import logging.handlers
from pathlib import Path

from rich.logging import RichHandler

import zerocom.config

LOG_LEVEL = logging.DEBUG if zerocom.config.DEBUG else logging.INFO
LOG_FILE = zerocom.config.LOG_FILE
LOG_FILE_MAX_SIZE = zerocom.config.LOG_FILE_MAX_SIZE
LOG_FORMAT = "%(asctime)s | %(name)s | %(levelname)7s | %(message)s"


def setup_logging() -> None:
    """Sets up logging library to use our log format and defines log levels."""
    root_log = logging.getLogger()
    log_formatter = logging.Formatter(LOG_FORMAT)

    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        handlers=[RichHandler(show_time=False)],
        datefmt="%Y-%m-%d %H:%M:%S",  # TODO: Add millisecond precision
    )

    if LOG_FILE is not None:
        file_handler = logging.handlers.RotatingFileHandler(Path(LOG_FILE), maxBytes=LOG_FILE_MAX_SIZE)
        file_handler.setFormatter(log_formatter)
        root_log.addHandler(file_handler)

    root_log.setLevel(LOG_LEVEL)
