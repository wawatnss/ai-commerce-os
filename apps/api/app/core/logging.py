"""Structured logging configuration."""

import logging
import sys

from config import settings


def configure_logging() -> None:
    """Configure root logger with a structured format."""
    log_format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format=log_format,
        handlers=[logging.StreamHandler(sys.stdout)],
    )
