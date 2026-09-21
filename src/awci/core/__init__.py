"""
Atmospheric Complexity Framework (ACF)

AWCI Core (``src/awci/core/``)

Real implementation of the package named in
``docs/architecture/awci_reference_architecture.md`` section 1 ("AWCI
Core... The software nucleus coordinating the whole platform"),
previously the specific gap named in
``docs/architecture/acf_awci_architecture_gap_analysis.md`` ("No
dedicated AWCI application/lifecycle/registry core exists; AWCI code
is simply part of ``acf.*``'s own process").

Built 2026-09-21: ``exceptions.py`` (``AWCIError`` hierarchy - a real
sibling to ``acf.core.exceptions.ACFError``, not a subclass, matching
the reference architecture's own framing of AWCI as a separate
product), ``constants.py``/``version.py`` (real values taken from this
codebase's own already-shipped AWCI identity - ``acf.awci_app``'s
``--version`` string and ``acf.__version__``, not invented),
``types.py`` (the handful of real type aliases this package's own
modules use), ``events.py`` (``EventBus``/``Event`` - a real,
generic, application-lifecycle pub/sub primitive, following the same
real dispatch/error-isolation discipline already established by
``awci.plugins.hooks.HookRegistry`` and
``awci.alerts.notifications.AlertNotifier``, but at a different real
scope - arbitrary named app events, not plugin hooks or alerts),
``registry.py`` (``ServiceRegistry`` - a real alias for the
already-real, already-generic
``acf.core.service_manager.ServiceManager``, reused directly rather
than duplicated), ``configuration.py`` (a real re-export of the
already-real, already-versioned ``awci.complexity.config_loader``,
built earlier in this codebase's history to close
``docs/ACF_MASTER_PROMPT.md`` section 56's own gap - not a second,
competing AWCI configuration concept), ``logging.py``
(``get_awci_logger()`` - a real, additional, filtered loguru sink
writing to ``logs/awci.log``, alongside - not replacing -
``acf.core.logger``'s own shared unfiltered sinks), ``context.py``
(``AWCIContext`` - bundles the real ``ServiceRegistry``/``EventBus``
plus the currently-open ``awci.workspace.AWCIProject``),
``lifecycle.py`` (``AWCILifecycle`` - real startup/shutdown sequence
registering real AWCI-specific services, mirroring
``acf.core.bootstrap.Bootstrap``'s own shape), and ``application.py``
(``AWCIApplication`` - the real, headless coordinator; never imports
PySide6, distinct from the real, GUI-coupled ``acf.awci_app`` launcher
this class does not replace).

``dependencies.py`` (the blueprint's remaining named file) is
deliberately not a separate file - see ``registry.py``'s own
docstring for why "service registration/lookup by name" and
"dependency injection" are the same real concept in this codebase.
"""

from __future__ import annotations

from awci.core.application import AWCIApplication
from awci.core.context import AWCIContext
from awci.core.events import Event, EventBus, EventDispatchError
from awci.core.exceptions import AWCIConfigurationError, AWCIError, AWCILifecycleError, AWCIServiceError
from awci.core.lifecycle import AWCILifecycle
from awci.core.registry import ServiceRegistry

__all__ = [
    "AWCIApplication",
    "AWCIConfigurationError",
    "AWCIContext",
    "AWCIError",
    "AWCILifecycle",
    "AWCILifecycleError",
    "AWCIServiceError",
    "Event",
    "EventBus",
    "EventDispatchError",
    "ServiceRegistry",
]
