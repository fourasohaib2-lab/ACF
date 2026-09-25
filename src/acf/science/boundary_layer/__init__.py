"""
Atmospheric Complexity Framework (ACF)

Boundary Layer Science Package

Migrated 2026-09-21 (Phase 6 of the ACF science/ per-domain
reorganization - see
docs/architecture/acf_awci_architecture_gap_analysis.md's own §4
section) from the single flat ``boundary_layer.py`` module directly
under ``acf.science``, matching the blueprint's own
``science/boundary_layer/`` layer. Real module name kept as-is.

``boundary_layer.py`` shares its own name with this package
(``acf.science.boundary_layer``) - a flat shim file at the old
``src/acf/science/boundary_layer.py`` path would be permanently
shadowed by this package directory and never actually importable (the
same real self-naming-collision bug already found and fixed for
``thermodynamics.py``/``stability.py``/``dynamics.py``/
``constants.py``/``radiation.py`` in §4a-§4e). There is no flat shim
for it; this ``__init__.py`` re-exports all 5 real names directly
instead.
"""

from acf.science.boundary_layer.boundary_layer import (
    VON_KARMAN,
    BowenRatio,
    FrictionVelocity,
    MoninObukhovLength,
    PBLHeight,
)

__all__ = [
    "BowenRatio",
    "FrictionVelocity",
    "MoninObukhovLength",
    "PBLHeight",
    "VON_KARMAN",
]
