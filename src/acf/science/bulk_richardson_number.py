"""Backward-compatible re-export.

Real module moved to ``acf.science.stability.bulk_richardson_number`` on
2026-09-21 (Phase 2 of the ACF science/ per-domain
reorganization - see
``src/acf/science/stability/__init__.py``'s own docstring
and
``docs/architecture/acf_awci_architecture_gap_analysis.md``).
Kept here so every existing ``acf.science.bulk_richardson_number`` import keeps
working unchanged.
"""

from acf.science.stability.bulk_richardson_number import *  # noqa: F401,F403
