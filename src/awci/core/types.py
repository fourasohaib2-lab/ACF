"""
Atmospheric Complexity Framework (ACF)

AWCI Core - Common Types

Real, minimal type aliases shared across ``awci.core`` - the
``types.py`` module named in
``docs/architecture/awci_reference_architecture.md`` section 1. Only
the aliases this package's own real modules (``events.py``,
``registry.py``) actually use - not a speculative, general-purpose
type-alias library.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from awci.core.events import Event

#: A real registered service's lookup name in ``ServiceRegistry``.
ServiceName = str

#: A real event's name in ``EventBus`` (e.g. "project_opened", "ready").
EventName = str

#: A real ``EventBus`` subscriber callback.
EventCallback = Callable[["Event"], None]

#: A real registered service instance - intentionally broad (services
#: in this codebase are heterogeneous real objects: a logger, a
#: config, a workspace manager), matching
#: ``acf.core.service_manager.ServiceManager``'s own real typing.
Service = Any
