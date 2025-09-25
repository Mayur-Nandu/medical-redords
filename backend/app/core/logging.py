from __future__ import annotations

import logging
import sys
from typing import Optional

from loguru import logger


class _InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        logger.bind(name=record.name).log(level, record.getMessage())


def configure_logging(level: str = "INFO") -> None:
    """Configure loguru as the central logger and intercept std logging.

    Avoid logging PHI; keep logs concise for compliance.
    """
    logger.remove()
    logger.add(
        sys.stdout,
        level=level,
        backtrace=False,
        diagnose=False,
        enqueue=True,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {name} | {message}",
    )

    intercept_handler = _InterceptHandler()
    logging.root.handlers = [intercept_handler]
    logging.root.setLevel(logging.NOTSET)

    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
        logging_logger = logging.getLogger(name)
        logging_logger.handlers = [intercept_handler]
        logging_logger.propagate = False


def get_logger() -> "logger.__class__":  # type: ignore[name-defined]
    return logger

