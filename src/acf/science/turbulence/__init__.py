"""
Atmospheric Complexity Framework (ACF)

Atmospheric Turbulence Science Package

Migrated 2026-09-21 (Phase 6 of the ACF science/ per-domain
reorganization - see
docs/architecture/acf_awci_architecture_gap_analysis.md's own §4
section) from the single flat ``wind_turbulence.py`` module directly
under ``acf.science``, matching the blueprint's own
``science/turbulence/`` layer. Real module name kept as-is (not
renamed to ``turbulence.py`` - there is no self-naming collision with
this package, so a real flat shim is kept too, unlike
``thermodynamics.py``/``stability.py``/``dynamics.py``/
``constants.py``/``radiation.py`` in §4a-§4e).
``acf.science.wind_turbulence`` is kept as a real backward-compatible
re-export.
"""

from acf.science.turbulence.wind_turbulence import (
    JET_STREAM_THRESHOLD_M_S,
    CATIndex,
    JetStream,
    TKEProduction,
)

__all__ = [
    "CATIndex",
    "JET_STREAM_THRESHOLD_M_S",
    "JetStream",
    "TKEProduction",
]
