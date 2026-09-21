"""
Atmospheric Complexity Framework (ACF)

Climate Science Package

Migrated 2026-09-21 (Phase 7 of the ACF science/ per-domain
reorganization - see
docs/architecture/acf_awci_architecture_gap_analysis.md's own §4
section) from the single flat ``climatology.py`` module directly under
``acf.science``, matching the blueprint's own ``science/climate/``
layer. Real module name kept as-is (not renamed to ``climate.py`` -
there is no self-naming collision with this package, so a real flat
shim is kept too, unlike ``thermodynamics.py``/``stability.py``/
``dynamics.py``/``constants.py``/``radiation.py``/``boundary_layer.py``
in §4a-§4f). ``acf.science.climatology`` is kept as a real
backward-compatible re-export.
"""

from acf.science.climate.climatology import ClimatologicalRecord, Climatology, HeatColdWave

__all__ = [
    "ClimatologicalRecord",
    "Climatology",
    "HeatColdWave",
]
