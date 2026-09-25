"""Backward-compatible re-export.

Real module moved to ``awci.hazards.orographic_froude`` on 2026-09-21
(Phase 1 of the AWCI separate-package migration - see
``src/awci/__init__.py``'s own docstring and
``docs/architecture/acf_awci_architecture_gap_analysis.md``). Kept
here so every existing ``acf.awci.orographic_froude`` import keeps
working unchanged.
"""

from awci.hazards.orographic_froude import *  # noqa: F401,F403
