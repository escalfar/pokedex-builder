import logging
from pathlib import Path

import pytest

from pokedex.logger import (
    DEFAULT_LOG_FILENAME,
    LOGGER_NAME,
    configure_logger,
    get_logger,
)


def test_configure_logger_creates_log_directory_and_file(
    tmp_path: Path,
) -> None:
    logs_directory = tmp_path / "logs"

    logger = configure_logger(logs_directory)
    logger.info("Pokédex logger test")

    log_path = logs_directory / DEFAULT_LOG_FILENAME

    assert logs_directory.is_dir()
    assert log_path.is_file()
    assert "Pokédex logger test" in log_path.read_text(encoding="utf-8")


def test_configure_logger_adds_console_and_file_handlers(
    tmp_path: Path,
) -> None:
    logger = configure_logger(tmp_path)

    assert len(logger.handlers) == 2
    assert any(
        isinstance(handler, logging.StreamHandler)
        and not isinstance(handler, logging.FileHandler)
        for handler in logger.handlers
    )
    assert any(isinstance(handler, logging.FileHandler) for handler in logger.handlers)


def test_configure_logger_does_not_duplicate_handlers(
    tmp_path: Path,
) -> None:
    first = configure_logger(tmp_path)
    second = configure_logger(tmp_path)

    assert first is second
    assert len(second.handlers) == 2


def test_configure_logger_uses_requested_level(tmp_path: Path) -> None:
    logger = configure_logger(tmp_path, level=logging.DEBUG)

    assert logger.level == logging.DEBUG
    assert all(handler.level == logging.DEBUG for handler in logger.handlers)


def test_configure_logger_rejects_empty_filename(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="cannot be empty"):
        configure_logger(tmp_path, filename="   ")


def test_get_logger_returns_application_logger() -> None:
    logger = get_logger()

    assert logger.name == LOGGER_NAME


def test_get_logger_returns_child_logger() -> None:
    logger = get_logger("cache")

    assert logger.name == f"{LOGGER_NAME}.cache"


def test_get_logger_rejects_empty_child_name() -> None:
    with pytest.raises(ValueError, match="cannot be empty"):
        get_logger("   ")
