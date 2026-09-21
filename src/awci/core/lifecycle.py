"""
Atmospheric Complexity Framework (ACF)

AWCI Core - Lifecycle

Real ``AWCILifecycle`` - the ``lifecycle.py`` module named in
``docs/architecture/awci_reference_architecture.md`` section 1.
Mirrors the real startup-sequence shape already established by
``acf.core.bootstrap.Bootstrap`` (register real services, then signal
readiness) but wires AWCI's own real components instead of ACF's
generic ones: ``awci.core.logging.get_awci_logger()`` (not
``acf.core.logger.get_logger()``) and
``awci.workspace.AWCIWorkspaceManager`` (not
``acf.workspace.manager.WorkspaceManager``) - the same real
"AWCI has its own separate real components" pattern already
established throughout this session (``.awciproj``/
``~/.awci/recent_projects.json``/``logs/awci.log``).

Deliberately does not discover/load plugins itself -
``awci.plugins.manager.PluginManager`` (built earlier this session,
real ``importlib``-based discovery) is the real plugin system; a
caller that wants plugins loaded at startup passes an already-
constructed ``PluginManager`` and this lifecycle registers it as a
service like any other real component, rather than this module
re-implementing plugin discovery a second time.
"""

from __future__ import annotations

from typing import Any

from awci.core.context import AWCIContext
from awci.core.exceptions import AWCILifecycleError
from awci.core.logging import get_awci_logger
from awci.workspace import AWCIWorkspaceManager


class AWCILifecycle:
    """Real AWCI application startup/shutdown sequence - registers real
    services into a real ``AWCIContext`` and emits real
    application-lifecycle events through its ``EventBus``."""

    def __init__(self) -> None:
        self.context = AWCIContext()
        self._started = False

    def start(self, extra_services: dict[str, Any] | None = None) -> AWCIContext:
        """
        Real startup: registers a real bound logger and a real
        ``AWCIWorkspaceManager`` into ``self.context.services``, plus
        any real ``extra_services`` a caller supplies (e.g. a
        pre-constructed ``awci.plugins.manager.PluginManager`` or a
        loaded ``awci.core.configuration.AWCIConfig``) - never
        fabricates a service that was not actually given or
        constructed here. Emits ``"starting"`` then ``"ready"`` on the
        real ``EventBus``. Returns the same real ``AWCIContext`` this
        instance owns.
        """
        logger = get_awci_logger()
        self.context.events.emit("starting")

        self.context.services.register("logger", logger)
        self.context.services.register("workspace", AWCIWorkspaceManager())

        for name, service in (extra_services or {}).items():
            self.context.services.register(name, service)

        logger.info("AWCI is ready.")
        self._started = True
        self.context.events.emit("ready")
        return self.context

    def stop(self) -> None:
        """Real shutdown: emits ``"stopping"`` then ``"stopped"``.
        Raises ``AWCILifecycleError`` if ``start()`` was never called -
        never silently no-ops on an invalid lifecycle transition."""
        if not self._started:
            raise AWCILifecycleError("Cannot stop an AWCI lifecycle that was never started.")

        self.context.events.emit("stopping")
        self._started = False
        self.context.events.emit("stopped")

    @property
    def is_started(self) -> bool:
        return self._started
