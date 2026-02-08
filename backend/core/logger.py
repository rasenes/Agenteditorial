"""
Système de logging centralisé avec rotation et formatage clean.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

from .config import CONFIG


class ColoredFormatter(logging.Formatter):
    """Formatter avec couleurs pour console."""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)


def get_logger(name: str) -> logging.Logger:
    """
    Obtient ou crée un logger pour un module.
    
    Args:
        name: Nom du logger (typiquement __name__)
    
    Returns:
        Logger configuré
    """
    logger = logging.getLogger(name)
    
    # Évite les duplications
    if logger.handlers:
        return logger
    
    # Niveau log
    level = getattr(logging, CONFIG.log_level.upper(), logging.INFO)
    logger.setLevel(level)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Format
    if CONFIG.debug:
        fmt = '[%(asctime)s] %(name)s - %(levelname)s - %(message)s'
    else:
        fmt = '%(levelname)s: %(message)s'
    
    formatter = ColoredFormatter(fmt, datefmt='%H:%M:%S')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (DEBUG mode only)
    if CONFIG.debug:
        log_dir = Path(__file__).parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(
            log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(fmt)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


# Logger par défaut
logger = get_logger(__name__)
