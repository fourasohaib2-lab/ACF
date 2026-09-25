"""Backward-compatible re-export.

Real module moved to ``awci.hazards.theta_e`` on 2026-09-21 (Phase 6
of the AWCI separate-package migration - see
``src/awci/hazards/__init__.py``'s own docstring and
``docs/architecture/acf_awci_architecture_gap_analysis.md``). Kept
here so every existing ``acf.awci.theta_e`` import keeps working
unchanged.
"""

from awci.hazards.theta_e import *  # noqa: F401,F403
