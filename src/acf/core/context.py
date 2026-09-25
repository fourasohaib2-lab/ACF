"""
Atmospheric Complexity Framework (ACF)

Core - Application Context

Real ``ApplicationContext`` - the ``context.py`` module named in
``docs/architecture/acf_awci_architecture_gap_analysis.md`` (row
``core/{...,context,...}.py``). A real, minimal container bundling
the real ``Registry`` (service lookup) and real ``EventBus``
(application events) - the same real "just holds already-real,
already-constructed pieces" shape as
``awci.core.context.AWCIContext``, at ACF's own general scope (no
``project``/workspace field - ACF's project concept is
``acf.workspace.Project``, already reachable through the registry
like any other real service, not hardcoded into this container).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from acf.core.events import EventBus
from acf.core.registry import Registry


@dataclass
class ApplicationContext:
    """Real application-wide state container - never computes
    anything itself, only holds the real, already-constructed pieces
    a caller wires together."""

    services: Registry = field(default_factory=Registry)
    events: EventBus = field(default_factory=EventBus)
