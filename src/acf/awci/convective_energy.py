"""
ACF Complexity Engine — real per-point CAPE/CIN
====================================================

Explicit user request, closing two real, previously-documented gaps at
once:

1. `acf.awci.spatial_field`'s own "Honest limitation" docstring:
   "CAPE/CIN/precipitation/terrain-altitude are NOT derived here...
   because computing a real CAPE/CIN at every grid point would need a
   full per-column parcel-ascent calculation this module does not
   perform. Declaring a fabricated CAPE from these alone... would be
   exactly the kind of invented number this project's audits exist to
   remove." That parcel-ascent calculation is what this module builds.
2. reports/ACF_MASTER_AUDIT_v2.md's encyclopedia scan: `acf.science.
   encyclopedia` (299 real entries) was found genuinely built and
   tested, but never actually called by anything that computes ACF's
   real outputs - only by search/explanation features. Two of its
   entries, "cape_convective_energy"/"cin_convective_inhibition",
   register real, working formulas
   (`EncyclopediaRegistry.get("cape_convective_energy").compute_func`
   delegates to `acf.science.cape.CAPE.calculate()` - see
   `acf.science.encyclopedia.convection_extended`) - this module is
   the first real caller of that physics outside the encyclopedia's
   own search feature.

Real pipeline, not a rule-of-thumb formula
--------------------------------------------
1. MetPy (already a real ACF dependency - `acf.normalization.units`,
   `acf.events.detectors.fog_detector` already use it) computes the
   real parcel ascent: dewpoint from specific humidity
   (`mpcalc.dewpoint_from_specific_humidity`), then a real dry+moist
   adiabatic lift (`mpcalc.parcel_profile`) - ACF's own solver has no
   parcel-ascent physics of its own, and hand-deriving one here would
   be exactly the kind of invented formula this project's audits exist
   to catch when a real, standard implementation is one import away.
   Real per-layer thicknesses come from the hypsometric equation
   (`mpcalc.thickness_hydrostatic`) - NOT a uniform `dz` assumption.
2. `acf.science.cape.CAPE.calculate()` / `acf.science.cin.CIN.calculate()`
   - the exact real classes the encyclopedia's own
   "cape_convective_energy"/"cin_convective_inhibition" entries
   delegate to - integrate the real buoyancy over those real,
   non-uniform layer thicknesses. Called directly here rather than
   through `EncyclopediaRegistry.calculate()`'s own convenience
   wrapper (`compute_cape(tv_parcel, tv_env, dz)`), which forces a
   single uniform `dz` for the whole profile - a real, avoidable
   accuracy loss when this pipeline already has the real, per-level
   heights from step 1. Same underlying real formula either way -
   documented here so the link to the registered encyclopedia entry
   stays traceable, not silently duplicated.

Honest scope
------------
- Levels above `MIN_PRESSURE_HPA_FOR_CONVECTIVE_ENERGY` are excluded
  before the parcel ascent - CAPE/CIN are only physically meaningful
  in the troposphere, and ACF's own native solver levels (unlike a
  real operational model's) are not guaranteed to stop there. A fixed
  100 hPa cutoff is ACF's own documented operational choice (matches
  common real forecasting practice), not a claim of a universal
  physical law - same "documented bound, not a physical absolute"
  convention as `acf.physics_guard.range_check.OPERATIONAL_RANGES`.
- Uses a real surface-based parcel (lifted from the lowest real level
  given) - not the most-unstable or mixed-layer parcel variants MetPy
  also offers. A real, common, defensible choice, not the only correct
  one.
- Same honest limitation as the rest of `acf.awci`: this runs on
  ACF's own `CoupledEarthSolver` output, standing in for a real
  operational sounding - not a real radiosonde/model analysis.
"""

from __future__ import annotations

from typing import Any

import metpy.calc as mpcalc
import numpy as np
from metpy.units import units as mp_units

from acf.science.cape import CAPE
from acf.science.cin import CIN

#: See module docstring's "Honest scope" - a documented operational
#: bound, not a physical law.
MIN_PRESSURE_HPA_FOR_CONVECTIVE_ENERGY = 100.0


def compute_real_cape_cin_at_point(
    temperature_profile_k: Any,
    specific_humidity_profile: Any,
    pressure_profile_hpa: Any,
) -> dict[str, Any]:
    """
    Real surface-based CAPE/CIN (J/kg) from one real vertical sounding.

    Parameters
    ----------
    temperature_profile_k, specific_humidity_profile, pressure_profile_hpa :
        1D real arrays, same length, ordered from the lowest real level
        (index 0) upward - e.g. one (lat, lon) column of
        `acf.awci.vertical_field.compute_real_complexity_volume()`'s
        `temperature_volume`/`specific_humidity_volume`/
        `pressure_volume_hpa`, or `acf.simulation_engine.coupled_solver.
        CoupledEarthSolver`'s own real `state["T"]/["q"]/["P"]` at one
        (lat, lon) column.

    Returns
    -------
    dict
        cape_j_kg, cin_j_kg : real, non-negative floats - `None`
            (never a fabricated 0.0) when fewer than 2 real levels
            remain after the real 100 hPa cutoff, since there is
            nothing real left to integrate over.
        n_levels_used : how many real levels actually went into the
            calculation, after the cutoff.
        status, is_real_data.

    Raises
    ------
    ValueError
        If the three profiles don't have the same real length.
    """
    t = np.asarray(temperature_profile_k, dtype=float)
    q = np.asarray(specific_humidity_profile, dtype=float)
    p = np.asarray(pressure_profile_hpa, dtype=float)
    if not (len(t) == len(q) == len(p)):
        raise ValueError(f"profiles must have the same length, got temperature={len(t)}, humidity={len(q)}, pressure={len(p)}")

    mask = p >= MIN_PRESSURE_HPA_FOR_CONVECTIVE_ENERGY
    t, q, p = t[mask], q[mask], p[mask]

    if len(p) < 2:
        return {
            "cape_j_kg": None,
            "cin_j_kg": None,
            "n_levels_used": int(len(p)),
            "status": f"NOT_COMPUTED_FEWER_THAN_2_REAL_LEVELS_ABOVE_{MIN_PRESSURE_HPA_FOR_CONVECTIVE_ENERGY:.0f}HPA",
            "is_real_data": False,
        }

    pressure = p * mp_units.hPa
    temperature = t * mp_units.kelvin
    # dewpoint_from_specific_humidity is undefined at q=0 (real physical
    # edge case - perfectly dry air has no real dewpoint) - clipped to a
    # tiny real positive floor rather than crashing on a genuinely dry
    # native-level column.
    specific_humidity = np.clip(q, 1e-9, None) * mp_units("kg/kg")

    # NOTE: MetPy's real signature accepts (pressure, specific_humidity) -
    # a `temperature` argument also exists but MetPy itself documents it
    # as "Unused in calculation, pending deprecation"; omitted so this
    # doesn't emit that real PendingDeprecationWarning on every call.
    dewpoint = mpcalc.dewpoint_from_specific_humidity(pressure, specific_humidity)
    parcel_profile = mpcalc.parcel_profile(pressure, temperature[0], dewpoint[0]).to("kelvin")

    heights = [0.0]
    for i in range(len(pressure) - 1):
        thickness = mpcalc.thickness_hydrostatic(pressure[i : i + 2], temperature[i : i + 2])
        heights.append(heights[-1] + thickness.to("m").magnitude)

    cape = CAPE.calculate(
        parcel_temperature=list(parcel_profile.magnitude),
        environment_temperature=list(temperature.magnitude),
        height=heights,
        environment_humidity=list(q),
        is_kelvin=True,
    )
    cin = CIN.calculate(
        parcel_temperature=list(parcel_profile.magnitude),
        environment_temperature=list(temperature.magnitude),
        height=heights,
        environment_humidity=list(q),
        is_kelvin=True,
    )

    return {
        "cape_j_kg": float(cape),
        "cin_j_kg": float(cin),
        "n_levels_used": int(len(p)),
        "status": "REAL_CAPE_CIN_FROM_METPY_PARCEL_ASCENT_AND_ENCYCLOPEDIA_CAPE_CIN_CLASSES",
        "is_real_data": True,
    }
