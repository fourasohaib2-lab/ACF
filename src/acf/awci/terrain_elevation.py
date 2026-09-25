"""Backward-compatible re-export.

Real module moved to ``awci.hazards.terrain_elevation`` on 2026-09-21
(Phase 8 of the AWCI separate-package migration - see
``src/awci/hazards/__init__.py``'s own docstring and
``docs/architecture/acf_awci_architecture_gap_analysis.md``). Kept
here so every existing ``acf.awci.terrain_elevation`` import keeps
working unchanged.
"""

from awci.hazards.terrain_elevation import *  # noqa: F401,F403
