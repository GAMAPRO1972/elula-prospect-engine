"""
integrations/ghl/logger.py

Central logging utilities for the GoHighLevel integration.
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from config.settings import settings


_LOGGER = None


def get_logger(name: str = "ghl") -> logging.Logger:
    global _LOGGER

    if _LOGGER is not None:
        return _LOGGER

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    if logger.handlers:
        _LOGGER = logger
        return logger

    log_path = Path(settings.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    )

    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.propagate = False

    _LOGGER = logger
    return logger


logger = get_logger()


def log_request(method: str, endpoint: str) -> None:
    logger.info("HTTP %s %s", method.upper(), endpoint)


def log_response(method: str, endpoint: str, status_code: int, elapsed_ms: int) -> None:
    logger.info(
        "HTTP %s %s -> %s (%sms)",
        method.upper(),
        endpoint,
        status_code,
        elapsed_ms,
    )


def log_retry(method: str, endpoint: str, attempt: int, max_attempts: int) -> None:
    logger.warning(
        "Retry %s/%s for %s %s",
        attempt,
        max_attempts,
        method.upper(),
        endpoint,
    )


def log_exception(message: str, exc: Exception) -> None:
    logger.exception("%s: %s", message, exc)
