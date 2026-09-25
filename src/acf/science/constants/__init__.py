"""
Atmospheric Complexity Framework (ACF)

Scientific Constants Package

Migrated 2026-09-21 (Phase 4 of the ACF science/ per-domain
reorganization - see
docs/architecture/acf_awci_architecture_gap_analysis.md's own §4
section) from the single flat ``constants.py`` module directly under
``acf.science``, matching the blueprint's own ``science/constants/``
layer. Real module name kept as-is.

``constants.py`` shares its own name with this package
(``acf.science.constants``) - a flat shim file at the old
``src/acf/science/constants.py`` path would be permanently shadowed by
this package directory and never actually importable (the same real
self-naming-collision bug already found and fixed for
``thermodynamics.py``/``stability.py``/``dynamics.py`` in
§4a/§4b/§4c). There is no flat shim for it; this ``__init__.py``
re-exports every real constant directly instead.
"""

from acf.science.constants.constants import (
    CP,
    CV,
    DEWPOINT_EXCEEDS_TEMPERATURE_TOLERANCE_K,
    EARTH_RADIUS,
    EPSILON,
    G,
    KAPPA,
    LF,
    LS,
    LV,
    MOLAR_MASS_DRY_AIR,
    MOLAR_MASS_WATER,
    OMEGA,
    P0,
    RD,
    RHO_ICE,
    RHO_WATER,
    RV,
    STANDARD_DENSITY,
    STANDARD_PRESSURE,
    STANDARD_TEMPERATURE,
    T0,
    UNIVERSAL_GAS_CONSTANT,
)

__all__ = [
    "CP",
    "CV",
    "DEWPOINT_EXCEEDS_TEMPERATURE_TOLERANCE_K",
    "EARTH_RADIUS",
    "EPSILON",
    "G",
    "KAPPA",
    "LF",
    "LS",
    "LV",
    "MOLAR_MASS_DRY_AIR",
    "MOLAR_MASS_WATER",
    "OMEGA",
    "P0",
    "RD",
    "RHO_ICE",
    "RHO_WATER",
    "RV",
    "STANDARD_DENSITY",
    "STANDARD_PRESSURE",
    "STANDARD_TEMPERATURE",
    "T0",
    "UNIVERSAL_GAS_CONSTANT",
]
