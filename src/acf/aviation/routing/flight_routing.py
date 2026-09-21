"""Backward-compatible re-export.

Real module moved to ``awci.knowledge.routing.flight_routing`` on
2026-09-21 (Phase 9 of the AWCI separate-package migration - see
``src/awci/knowledge/__init__.py``'s own docstring and
``docs/architecture/acf_awci_architecture_gap_analysis.md``). Kept here
so every existing ``acf.aviation.routing.flight_routing`` import keeps
working unchanged.
"""

from awci.knowledge.routing.flight_routing import *  # noqa: F401,F403
