"""
Atmospheric Complexity Framework (ACF)

Atmospheric Dynamics Science Package

Migrated 2026-09-21 (Phase 3 of the ACF science/ per-domain
reorganization - see
docs/architecture/acf_awci_architecture_gap_analysis.md's own §4
section) from 6 flat modules directly under ``acf.science`` into this
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
"""

from acf.science.dynamics.divergence import Divergence
from acf.science.dynamics.dynamics import Dynamics
from acf.science.dynamics.fronts import AirMass, FrontMovement, FrontType
from acf.science.dynamics.frontogenesis import Frontogenesis
from acf.science.dynamics.potential_vorticity import PotentialVorticity
from acf.science.dynamics.vorticity import Vorticity

__all__ = [
    "AirMass",
    "Divergence",
    "Dynamics",
    "FrontMovement",
    "FrontType",
    "Frontogenesis",
    "PotentialVorticity",
    "Vorticity",
]
