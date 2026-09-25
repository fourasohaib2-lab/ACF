"""Backward-compatible re-export.

Real module moved to ``acf.science.thermodynamics.virtual_potential_temperature`` on
2026-09-21 (Phase 1 of the ACF science/ per-domain
reorganization - see
``src/acf/science/thermodynamics/__init__.py``'s own docstring
and
``docs/architecture/acf_awci_architecture_gap_analysis.md``).
Kept here so every existing ``acf.science.virtual_potential_temperature`` import keeps
working unchanged.
"""

from acf.science.thermodynamics.virtual_potential_temperature import *  # noqa: F401,F403
