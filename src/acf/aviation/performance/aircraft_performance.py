"""Backward-compatible re-export.

Real module moved to ``awci.knowledge.performance.aircraft_performance``
on 2026-09-21 (Phase 9 of the AWCI separate-package migration - see
``src/awci/knowledge/__init__.py``'s own docstring and
``docs/architecture/acf_awci_architecture_gap_analysis.md``). Kept here
so every existing ``acf.aviation.performance.aircraft_performance``
import keeps working unchanged.
"""

from awci.knowledge.performance.aircraft_performance import *  # noqa: F401,F403
