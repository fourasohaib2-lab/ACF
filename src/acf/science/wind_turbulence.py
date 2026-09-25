"""Backward-compatible re-export.

Real module moved to ``acf.science.turbulence.wind_turbulence`` on
2026-09-21 (Phase 6 of the ACF science/ per-domain reorganization -
see ``src/acf/science/turbulence/__init__.py``'s own docstring and
``docs/architecture/acf_awci_architecture_gap_analysis.md``). Kept
here so every existing ``acf.science.wind_turbulence`` import keeps
working unchanged.
"""

from acf.science.turbulence.wind_turbulence import *  # noqa: F401,F403
