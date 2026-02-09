from __future__ import annotations

import logging
import sys

from .config import SETTINGS


_CONFIGURED = False



def configure_logging() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return

    level = getattr(logging, SETTINGS.app.log_level.upper(), logging.INFO)
    fmt = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    logging.basicConfig(level=level, format=fmt, handlers=[logging.StreamHandler(sys.stdout)])
    _CONFIGURED = True



def get_logger(name: str) -> logging.Logger:
    configure_logging()
    return logging.getLogger(name)
