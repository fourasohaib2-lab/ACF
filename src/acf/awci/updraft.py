"""Backward-compatible re-export.

Real module moved to ``awci.hazards.updraft`` on 2026-09-21 (Phase 7
of the AWCI separate-package migration - see
``src/awci/hazards/__init__.py``'s own docstring and
``docs/architecture/acf_awci_architecture_gap_analysis.md``). Kept
here so every existing ``acf.awci.updraft`` import keeps working
unchanged.
"""

from awci.hazards.updraft import *  # noqa: F401,F403
