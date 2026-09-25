"""
Atmospheric Complexity Framework (ACF)

AWCI Core - Application

Real ``AWCIApplication`` - the ``application.py`` module named in
``docs/architecture/awci_reference_architecture.md`` section 1. A
real, headless application-lifecycle coordinator - "configuration,
lifecycle, events, dependency injection, plugin registry, AWCI
context, common types, error handling, logging. It does not itself
compute turbulence or icing" (that section's own responsibility list).

Distinct from ``acf.awci_app`` (the real, GUI-coupled standalone
launcher - constructs a ``QApplication``/``AWCIDashboardWindow``,
handles ``--version``/``--help``). This class never imports PySide6
and is usable headless (a script, a test, a future web/API front end)
- ``acf.awci_app.run()`` is a real, different, GUI-specific entry
point this class does not replace and is not wired into (same
disclosed "headless core, separate GUI launcher" split already used
throughout this session for ``awci.decision``/``awci.alerts``/
``awci.plugins``).
"""

from __future__ import annotations

from awci.core.constants import APP_FULL_NAME, APP_NAME
from awci.core.context import AWCIContext
from awci.core.lifecycle import AWCILifecycle
from awci.core.version import __version__


class AWCIApplication:
    """Real, headless AWCI application - owns one real
    ``AWCILifecycle`` and exposes its resulting ``AWCIContext``."""

    def __init__(self) -> None:
        self.name = APP_NAME
        self.full_name = APP_FULL_NAME
        self.version = __version__
        self._lifecycle = AWCILifecycle()

    def start(self) -> AWCIContext:
        """Real startup - delegates to ``AWCILifecycle.start()``.
        Returns the real ``AWCIContext`` a caller uses to reach
        registered services (logger, workspace manager, ...)."""
        return self._lifecycle.start()

    def stop(self) -> None:
        """Real shutdown - delegates to ``AWCILifecycle.stop()``."""
        self._lifecycle.stop()

    @property
    def context(self) -> AWCIContext:
        return self._lifecycle.context

    @property
    def is_running(self) -> bool:
        return self._lifecycle.is_started
