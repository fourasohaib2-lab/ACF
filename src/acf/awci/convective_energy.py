"""Backward-compatible re-export.

Real module moved to ``awci.hazards.convective_energy`` on 2026-09-21
(Phase 6 of the AWCI separate-package migration - see
``src/awci/hazards/__init__.py``'s own docstring and
``docs/architecture/acf_awci_architecture_gap_analysis.md``). Kept
here so every existing ``acf.awci.convective_energy`` import keeps
working unchanged.
"""

from awci.hazards.convective_energy import *  # noqa: F401,F403
