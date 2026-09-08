"""
Atmospheric Complexity Framework (ACF)
Logger Module
"""

import sys
from pathlib import Path

from loguru import logger

# Dossier des journaux
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "acf.log"

# Supprime les handlers par défaut
logger.remove()

# Affichage dans le terminal
logger.add(
    sys.stdout,
    level="INFO",
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan> - "
    "<level>{message}</level>",
)

# Fichier de log
logger.add(
    LOG_FILE,
    level="DEBUG",
    rotation="10 MB",
    retention="30 days",
    encoding="utf-8",
)


def get_logger():
    """Retourne le logger partagé du projet."""
    return logger
