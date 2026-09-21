"""Backward-compatible re-export.

Real module moved to ``awci.hazards.volcanic_ash`` on 2026-09-21
(Phase 1 of the AWCI separate-package migration - see
``src/awci/__init__.py``'s own docstring and
``docs/architecture/acf_awci_architecture_gap_analysis.md``). Kept
here so every existing ``acf.awci.volcanic_ash`` import keeps working
unchanged.
"""

from awci.hazards.volcanic_ash import *  # noqa: F401,F403
