"""
Atmospheric Complexity Framework (ACF)

AWCI Core - Logging

Real AWCI-specific loguru sink - the ``logging.py`` module named in
``docs/architecture/awci_reference_architecture.md`` section 1. Reuses
``loguru`` (already a real project dependency via
``acf.core.logger``) and the exact same real process-wide
``loguru.logger`` singleton - not a second, independent logging
library or configuration mechanism.

Real, disclosed design: ``acf.core.logger`` already adds two unfiltered
sinks (stdout, ``logs/acf.log``) that catch every message from any
caller, AWCI included - this module does not touch or remove those.
It adds one additional real sink, ``logs/awci.log``, filtered to only
messages logged through ``get_awci_logger()`` (bound with
``app="awci"``), so an operator running the standalone AWCI
application (``acf.awci_app``) gets its own dedicated log file
alongside the shared one, mirroring the same separate-artifact
convention ``awci.workspace.manager.AWCIWorkspaceManager`` already
established for its own ``~/.awci/recent_projects.json``.
"""

from __future__ import annotations

from pathlib import Path

from loguru import logger as _logger

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "awci.log"

_logger.add(
    LOG_FILE,
    level="DEBUG",
    rotation="10 MB",
    retention="30 days",
    encoding="utf-8",
    filter=lambda record: record["extra"].get("app") == "awci",
)


def get_awci_logger():
    """Real, bound logger - every message logged through the returned
    object is tagged ``app="awci"``, so it lands in both the shared
    unfiltered sinks (stdout, ``logs/acf.log``) and this module's own
    filtered ``logs/awci.log`` sink."""
    return _logger.bind(app="awci")
