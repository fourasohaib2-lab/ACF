"""Backward-compatible re-export.

Real module moved to ``acf.science.convection.severe_weather`` on
2026-09-21 (Phase 7 of the ACF science/ per-domain
reorganization - see
``src/acf/science/convection/__init__.py``'s own docstring and
``docs/architecture/acf_awci_architecture_gap_analysis.md``).
Kept here so every existing ``acf.science.severe_weather`` import keeps
working unchanged.
"""

from acf.science.convection.severe_weather import *  # noqa: F401,F403
