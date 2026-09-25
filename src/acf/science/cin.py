"""Backward-compatible re-export.

Real module moved to ``acf.science.convection.cin`` on
2026-09-21 (Phase 2 of the ACF science/ per-domain
reorganization - see
``src/acf/science/convection/__init__.py``'s own docstring
and
``docs/architecture/acf_awci_architecture_gap_analysis.md``).
Kept here so every existing ``acf.science.cin`` import keeps
working unchanged.
"""

from acf.science.convection.cin import *  # noqa: F401,F403
