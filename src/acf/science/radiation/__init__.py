"""
Atmospheric Complexity Framework (ACF)

Radiation Science Package

Migrated 2026-09-21 (Phase 5 of the ACF science/ per-domain
reorganization - see
docs/architecture/acf_awci_architecture_gap_analysis.md's own §4
section) from the single flat ``radiation.py`` module directly under
``acf.science``, matching the blueprint's own ``science/radiation/``
layer. Real module name kept as-is.

``radiation.py`` shares its own name with this package
(``acf.science.radiation``) - a flat shim file at the old
``src/acf/science/radiation.py`` path would be permanently shadowed by
this package directory and never actually importable (the same real
self-naming-collision bug already found and fixed for
``thermodynamics.py``/``stability.py``/``dynamics.py``/``constants.py``
in §4a-§4d). There is no flat shim for it; this ``__init__.py``
re-exports all 4 real classes directly instead.
"""

from acf.science.radiation.radiation import (
    BOLTZMANN_K,
    PLANCK_H,
    SOLAR_CONSTANT_S0,
    SPEED_OF_LIGHT_C,
    STEFAN_BOLTZMANN_SIGMA,
    BeerLambert,
    PlanckLaw,
    SolarPosition,
    StefanBoltzmann,
)

__all__ = [
    "BOLTZMANN_K",
    "BeerLambert",
    "PLANCK_H",
    "PlanckLaw",
    "SOLAR_CONSTANT_S0",
    "SPEED_OF_LIGHT_C",
    "STEFAN_BOLTZMANN_SIGMA",
    "SolarPosition",
    "StefanBoltzmann",
]
