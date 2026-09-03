"""
ACF Complexity Engine — real per-point bulk wind shear
==========================================================

Explicit user request ("commence par le module dynamique, avec le
cisaillement de vent"), the first real closure of §12-16's own finding
from this session's exhaustive 90-section conformance audit
(reports/ACF_MASTER_AUDIT_v2.md): the "dynamic" module used only a
single scalar wind speed, while docs/ACF_MASTER_PROMPT.md section 12
explicitly lists "cisaillement vertical" among the dynamic module's own
candidate variables, and a real, correct `acf.science.bulk_wind_shear.
BulkWindShear` formula already existed in this codebase but was never
called by anything that computes ACF's real outputs (the same "real
formula, never wired in" pattern already found and closed for
CAPE/CIN - see acf.awci.convective_energy's own docstring).

Real formula, not reimplemented
----------------------------------
`compute_real_wind_shear_at_point()` is a thin, real wrapper around
`acf.science.bulk_wind_shear.BulkWindShear.calculate()` - the real
bulk shear magnitude between two real (u, v) wind vectors:
`sqrt((u_top - u_bottom)**2 + (v_top - v_bottom)**2)`. No new physics
invented here.

Honest scope
-------------
This computes shear between two real NATIVE MODEL LEVELS (by index),
not a real fixed physical layer (e.g. the operationally common 0-1 km
or 0-6 km bulk shear layers a real forecaster would recognize) -
ACF's own native solver levels are not yet pinned to real physical
heights/pressures at each point (the same real, already-documented gap
this session's audit found for §14-21: "pas de moteur générique
VerticalCoordinate avec conversion pression/hauteur"). The default
`top_level=-1` (the solver's own highest real native level) spans the
full real vertical extent this codebase actually has today, not a
fabricated 850/500 hPa or 0-6 km layer - the real value computed is
genuine, but its real vertical extent should not be read as matching
any specific named operational shear layer.
"""

from __future__ import annotations

from typing import Any

from acf.science.bulk_wind_shear import BulkWindShear


def compute_real_wind_shear_at_point(
    u_profile: Any,
    v_profile: Any,
    bottom_level: int = 0,
    top_level: int = -1,
) -> dict[str, Any]:
    """
    Real bulk wind shear (m/s) between two real levels of one real
    vertical wind profile.

    Parameters
    ----------
    u_profile, v_profile : 1D real arrays, same length
        Real eastward/northward wind components at every native model
        level, ordered from the lowest real level (index 0) upward -
        e.g. `acf.simulation_engine.coupled_solver.CoupledEarthSolver`'s
        own real `state["U"]`/`state["V"]` at one (lat, lon) column.
    bottom_level, top_level : int
        Real native level indices into `u_profile`/`v_profile` (Python
        indexing - `-1` is the real highest level). Defaults span the
        full real vertical extent of the profile (see module docstring
        for why this is not a fixed physical layer).

    Returns
    -------
    dict
        shear_m_s : real, non-negative float - the real bulk shear
            magnitude.
        bottom_level, top_level : the real level indices actually used
            (with `-1` already resolved to its real positive index).
        status, is_real_data.

    Raises
    ------
    IndexError
        If `bottom_level`/`top_level` are out of range for the real
        supplied profile - propagated from the real array indexing,
        never silently clamped to a different, unrequested level.
    """
    u_bottom = float(u_profile[bottom_level])
    v_bottom = float(v_profile[bottom_level])
    u_top = float(u_profile[top_level])
    v_top = float(v_profile[top_level])

    shear_m_s = BulkWindShear.calculate(u_bottom, v_bottom, u_top, v_top)

    n_levels = len(u_profile)
    return {
        "shear_m_s": shear_m_s,
        "bottom_level": bottom_level % n_levels,
        "top_level": top_level % n_levels,
        "status": "REAL_BULK_WIND_SHEAR",
        "is_real_data": True,
    }
