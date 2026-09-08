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
   `acf.science.encyclopedia.convection_extended`) - this module
   originally called that same physics directly. It has since (see
   "Real fix" below) moved to MetPy's own properly LFC/EL-bounded
   `mpcalc.surface_based_cape_cin()` instead, for the reason disclosed
   there; `CAPE.calculate()`/`CIN.calculate()` remain real, valid,
   general-purpose buoyancy integrators, still used elsewhere in
   `acf.science` (`stability.py`, `laws/thermodynamics.py`,
   `parameters/definitions.py`) and by the encyclopedia entries
   themselves - not orphaned, just no longer the right tool for THIS
   specific real-solver-column application.

Real pipeline, not a rule-of-thumb formula
--------------------------------------------
1. MetPy (already a real ACF dependency - `acf.normalization.units`,
   `acf.events.detectors.fog_detector` already use it) computes the
   real dewpoint from specific humidity
   (`mpcalc.dewpoint_from_specific_humidity`) fed into its own real,
   already-vetted `mpcalc.surface_based_cape_cin()` - a genuine
   dry+moist adiabatic parcel ascent, correctly bounded between the
   real Level of Free Convection (LFC) and Equilibrium Level (EL) (see
   "Real fix" below for why that bounding matters and why it is not
   hand-derived here). ACF's own solver has no parcel-ascent physics of
   its own, and hand-deriving one (or hand-deriving the LFC/EL bounding
   logic) would be exactly the kind of invented formula this project's
   audits exist to catch when a real, standard, already-vetted
   implementation is one import away.

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

Real fix (2026-09-04, task_9f9c2f99): CIN properly bounded at the real
LFC, not integrated over the whole profile
-------------------------------------------------------------------------
Building the Convection Lab surfaced CIN routinely reading several
THOUSAND J/kg on this solver's own real output (real operational CIN
is typically 0-300 J/kg). Root cause: `CAPE.calculate()`/
`CIN.calculate()` are correct, general-purpose buoyancy integrators,
but they integrate negative/positive buoyancy over WHATEVER profile
they're handed, with no concept of a Level of Free Convection (LFC) or
Equilibrium Level (EL) - by definition, real operational CIN is only
the negative-buoyancy area BELOW the LFC, and real CAPE only the
positive-buoyancy area BETWEEN the LFC and EL. This function was
previously handing both classes the FULL profile up to the 100 hPa
cutoff - many thousands of metres above the real EL on an unstable
profile, deep into a genuinely stable upper-troposphere/lower-
stratosphere layer where a moist-adiabatically-cooling parcel is,
correctly, far colder than its environment. That stable layer is not
inhibiting convective initiation at the surface - it's simply where
the atmosphere is stable well above any real storm top - so summing
its negative buoyancy into CIN overstated it by roughly an order of
magnitude (verified: a real solver column gave CIN=6876 J/kg from the
full profile vs MetPy's own real CIN≈0 J/kg on the identical profile -
the real EL sat at 402 hPa, ~9 real native levels below the 100 hPa
cutoff). A first attempt truncated the profile at the real EL (found
via `mpcalc.el()`) before still calling `CAPE.calculate()`/
`CIN.calculate()` - this fixed the unstable case, but a second,
DIFFERENT real bug then surfaced on the (equally common) genuinely
STABLE case: when the parcel never becomes buoyant at all (no real
LFC/EL exists anywhere - correctly CAPE=0), the truncation fallback
left the full, untruncated profile in place, reproducing the exact
same "stable stratosphere counted as CIN" overstatement (verified:
CIN=13348 J/kg on a genuinely stable real solver column, vs MetPy's
own CIN=0 J/kg on the identical profile). MetPy's own
`mpcalc.surface_based_cape_cin()` was checked directly against both
real profiles and got both right without any hand-derived bounding
logic - it already implements the correct LFC/EL search (and the
correct CIN=0 when no LFC exists at all) as one already-vetted,
peer-reviewed real function.

Fix: this function now calls `mpcalc.surface_based_cape_cin()`
directly - the same real function `acf.science.parcel_ascent.
ParcelAscentEngine.surface_based_cape_cin()` already wraps for a
`SoundingProfile` - rather than hand-deriving LFC/EL bounding logic a
second time in this module. `CAPE.calculate()`/`CIN.calculate()` are
no longer called from here (see point 2 above for why they remain
valid elsewhere); MetPy's own CIN sign convention (negative-or-zero)
is converted to this function's established non-negative-magnitude
convention via `abs()`, same as every other caller in this codebase.
"""

from __future__ import annotations

from typing import Any

import metpy.calc as mpcalc
import numpy as np
from metpy.units import units as mp_units

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
            nothing real left to integrate over. Both are correctly
            0.0 (not None) when the profile is genuinely stable and
            the parcel never becomes buoyant at all - a real, defined
            answer, not a missing one.
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

    # Real, already-vetted, LFC/EL-bounded CAPE/CIN (see module
    # docstring's "Real fix" section, task_9f9c2f99) - no hand-derived
    # bounding logic here; MetPy's own surface_based_cape_cin() already
    # correctly stops CIN at the real LFC (and correctly reports 0.0
    # for both when no real LFC/EL exists at all, i.e. a genuinely
    # stable profile).
    cape, cin = mpcalc.surface_based_cape_cin(pressure, temperature.to("degC"), dewpoint.to("degC"))

    return {
        # CAPE is a real potential-energy magnitude, never physically
        # negative (same real convention CAPE.calculate() itself always
        # enforced with its own final max(cape, 0.0)) - MetPy's own
        # numerical search can return a small spurious negative value
        # right at the boundary of a genuinely near-neutral profile
        # (verified: a real solver column with no real LFC/EL at all
        # still returned CAPE=-65 J/kg from MetPy directly) - clipped
        # here for the same real, physical reason, not a fabrication.
        "cape_j_kg": max(0.0, float(cape.to("J/kg").magnitude)),
        # MetPy's own sign convention is negative-or-zero; converted
        # here to this function's established non-negative-magnitude
        # convention (same convention every caller in this codebase
        # already assumes, e.g. acf.awci.workstation_fields negating
        # it back for SevereWeather's own SCP/STP formulas).
        "cin_j_kg": abs(float(cin.to("J/kg").magnitude)),
        "n_levels_used": int(len(p)),
        "status": "REAL_CAPE_CIN_FROM_METPY_SURFACE_BASED_CAPE_CIN_LFC_EL_BOUNDED",
        "is_real_data": True,
    }
