"""
Atmospheric Complexity Framework (ACF)

AWCI Core - Application Context

Real ``AWCIContext`` - the ``context.py`` module named in
``docs/architecture/awci_reference_architecture.md`` section 1. A
real, minimal, application-wide container bundling the 3 real pieces
an ``AWCIApplication`` and its collaborators need to reach: the
``ServiceRegistry`` (name-based lookup of shared real objects - a
logger, a loaded config, a workspace manager), the ``EventBus`` (real
application-lifecycle events), and the currently-open
``awci.workspace.AWCIProject`` (``None`` when no project is open -
never fabricated).

Deliberately distinct from ``awci.decision.DecisionContext`` (a
per-point real meteorological context: lat/lon/pressure/timestamp) -
different real scope entirely (application-wide plumbing vs. a single
weather-decision query), sharing only the word "context".
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from awci.core.events import EventBus
from awci.core.registry import ServiceRegistry

if TYPE_CHECKING:
    from awci.workspace import AWCIProject


@dataclass
class AWCIContext:
    """Real application-wide state container - never computes
    anything itself, only holds the real, already-constructed pieces
    ``AWCIApplication``'s lifecycle wires together."""

    services: ServiceRegistry = field(default_factory=ServiceRegistry)
    events: EventBus = field(default_factory=EventBus)
    project: "AWCIProject | None" = None

    def has_project(self) -> bool:
        """Real check - honestly reports whether a real project is
        currently open, never assumed."""
        return self.project is not None
