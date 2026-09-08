"""HPC Logger and Telemetry Tracing (ACF-HPC-001)."""

import logging

logger = logging.getLogger("acf.hpc_connector")
logger.setLevel(logging.INFO)

if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter("[%(asctime)s][ACF-HPC][%(levelname)s] %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)


def log_hpc_event(level: str, message: str) -> None:
    """Log an HPC event message."""
    lvl = level.upper()
    if lvl == "DEBUG":
        logger.debug(message)
    elif lvl == "WARNING":
        logger.warning(message)
    elif lvl == "ERROR":
        logger.error(message)
    else:
        logger.info(message)
