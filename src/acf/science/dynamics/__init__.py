"""
Atmospheric Complexity Framework (ACF)

Atmospheric Dynamics Science Package

Migrated 2026-09-21 (Phase 3, and extended in Phase 7, of the ACF
science/ per-domain reorganization - see
docs/architecture/acf_awci_architecture_gap_analysis.md's own §4
section) from flat modules directly under ``acf.science`` into this
subpackage, matching the blueprint's own ``science/dynamics/`` layer.
Real module names kept as-is. ``acf.science.<module>`` is kept as a
real backward-compatible re-export for every one of them, except
``dynamics.py`` itself.

``dynamics.py`` shares its own name with this package
(``acf.science.dynamics``) - a flat shim file at the old
``src/acf/science/dynamics.py`` path would be permanently shadowed by
this package directory and never actually importable (a regular
package always shadows a same-named module in Python's import
resolution - the same real bug already found and fixed for
``thermodynamics.py``/``stability.py`` in §4a/§4b). There is no flat
shim for it; this ``__init__.py`` re-exports ``Dynamics`` directly
instead.

Phase 7 added ``synoptic.py`` (Coriolis/geostrophic/thermal-wind/
Ertel-PV formulations - already depended on ``potential_vorticity.py``,
moved here in Phase 3), ``cyclones.py`` (a real but mixed-role module -
gradient wind balance and Rossby radius are dynamics formulations,
``BruntVaisalaFrequency`` is arguably a stability concept too, and
``SaffirSimpson`` is a classification scale rather than a formula -
kept together as the one coherent file it already was rather than
fragmented across packages, a disclosed placement decision), and
``wind.py`` (basic wind-vector speed/direction kinematics).
"""

from acf.science.dynamics.cyclones import (
    BOMB_REFERENCE_LATITUDE_DEG,
    Bombogenesis,
    BruntVaisalaFrequency,
    GradientWind,
    RossbyRadius,
    SaffirSimpson,
)
from acf.science.dynamics.divergence import Divergence
from acf.science.dynamics.dynamics import Dynamics
from acf.science.dynamics.fronts import AirMass, FrontMovement, FrontType
from acf.science.dynamics.frontogenesis import Frontogenesis
from acf.science.dynamics.potential_vorticity import PotentialVorticity
from acf.science.dynamics.synoptic import (
    EARTH_RADIUS_M,
    Coriolis,
    ErtelPotentialVorticity,
    GeostrophicWind,
    ThermalWind,
)
from acf.science.dynamics.vorticity import Vorticity
from acf.science.dynamics.wind import Wind

__all__ = [
    "AirMass",
    "BOMB_REFERENCE_LATITUDE_DEG",
    "Bombogenesis",
    "BruntVaisalaFrequency",
    "Coriolis",
    "Divergence",
    "Dynamics",
    "EARTH_RADIUS_M",
    "ErtelPotentialVorticity",
    "FrontMovement",
    "FrontType",
    "Frontogenesis",
    "GeostrophicWind",
    "GradientWind",
    "PotentialVorticity",
    "RossbyRadius",
    "SaffirSimpson",
    "ThermalWind",
    "Vorticity",
    "Wind",
]
