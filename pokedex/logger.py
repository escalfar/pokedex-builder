from __future__ import annotations

import logging
from pathlib import Path

LOGGER_NAME = "pokedex_builder"
DEFAULT_LOG_FILENAME = "pokedex.log"
DEFAULT_LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configure_logger(
    logs_directory: Path,
    *,
    level: int = DEFAULT_LOG_LEVEL,
    filename: str = DEFAULT_LOG_FILENAME,
) -> logging.Logger:
    """Configure and return the application's central logger.

    The logger writes messages to both the console and a UTF-8 log file.
    Calling this function more than once replaces the existing handlers,
    preventing duplicate log messages.
    """
    if not filename.strip():
        raise ValueError("Log filename cannot be empty.")

    try:
        logs_directory.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise RuntimeError(
            f"Unable to create logs directory: {logs_directory}"
        ) from error

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(level)
    logger.propagate = False

    _remove_handlers(logger)

    formatter = logging.Formatter(
        fmt=LOG_FORMAT,
        datefmt=DATE_FORMAT,
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    log_path = logs_directory / filename

    try:
        file_handler = logging.FileHandler(
            filename=log_path,
            encoding="utf-8",
        )
    except OSError as error:
        raise RuntimeError(f"Unable to create log file: {log_path}") from error

    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    """Return the application logger or one of its child loggers."""
    if name is None:
        return logging.getLogger(LOGGER_NAME)

    normalized_name = name.strip()

    if not normalized_name:
        raise ValueError("Logger name cannot be empty.")

    return logging.getLogger(f"{LOGGER_NAME}.{normalized_name}")


def _remove_handlers(logger: logging.Logger) -> None:
    """Close and remove every handler currently attached to a logger."""
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()
