"""
ACF Complexity Engine — real per-point ceiling (cloud-base height) estimate
=============================================================================

Closes part of the gap identified in the cross-check of AWCI against the
project's own "AWCI — programme complet" specification (post-model4d
audit, 2026-09-11): "visibilité et plafond" had zero diagnostic anywhere
in `acf.awci` - neither a module in `AWCICalculator.calculate_module_
scores()` nor a per-point helper like `theta_e.py`/`orographic_froude.py`.
This module is the ceiling half of that gap; `acf.awci.visibility` is the
companion visibility half.

Real formula, composed from already-existing, correct pieces - not
reimplemented
-----------------------------------------------------------------------
1. `acf.science.thermodynamics.Thermodynamics.calculate_relative_humidity()`
   - the same real relative-humidity formula `acf.awci.theta_e` already
   reuses.
2. `acf.science.dewpoint.DewPoint.calculate()` - the same real
   Magnus-Tetens dewpoint formula (Alduchov & Eskridge 1996
   coefficients) `acf.awci.theta_e` already reuses.
3. The lifting condensation level (LCL) height approximation:
   `height_m ≈ 125 × (T_c − Td_c)`. This is a standard, widely-used
   first-order meteorological approximation, not an ACF invention: it
   follows directly from two real, independent lapse rates - the dry
   adiabatic lapse rate (≈9.8 K/km, exact for an unsaturated parcel)
   and the empirical decrease of dewpoint with height along a rising
   unsaturated parcel (≈1.8-2 K/km) - whose difference (≈8 K/km) gives
   a convergence rate of dewpoint depression to zero (saturation) of
   about 125 m per °C of surface dewpoint depression. It is an
   approximation of the true adiabatic LCL, not an exact solution of
   the saturation vapor-pressure equations, and it estimates the
   height at which a rising surface-based parcel would first saturate
   - not a direct observation of an actual cloud base, which can be
   higher (subsidence, capping inversion) or simply absent (no cloud
   at all, in which case this height is honestly meaningless as a
   "ceiling" and is flagged as such by the caller via cloud-cover
   context this module does not have).

Honest scope
-------------
`compute_real_ceiling_at_point()` returns `ceiling_height_m=None` (never
a fabricated meters value) when the real computed relative humidity is
non-positive - identical edge case, and identical honest-None
discipline, to `acf.awci.theta_e.compute_real_theta_e_at_point()`.

This module does NOT know whether a cloud genuinely exists at the
estimated height - it estimates where the lowest cloud base WOULD be if
one forms from a surface-based parcel. A caller working in genuinely
clear-sky conditions should not present this value to an end user as an
observed ceiling; `AWCICalculator`'s own module docstring for the
`ceiling` module (see `calculator.py`) discloses this same limitation
at its point of use.

Flight-category classification (LIFR/IFR/MVFR/VFR)
-----------------------------------------------------
The real ceiling-height thresholds used by
`classify_ceiling_category()` (152.4 m / 500 ft, 304.8 m / 1000 ft,
914.4 m / 3000 ft) are the real, standard ceiling-only cutoffs of the
flight-category convention used operationally by the U.S. FAA / NOAA
Aviation Weather Center (LIFR / IFR / MVFR / VFR) - not an ACF
invention. The real, full FAA definition of each category also
incorporates surface visibility (the lower of the two components
always governs); this function classifies ceiling alone, honestly
named `ceiling_category` rather than `flight_category`, so it is never
mistaken for the complete FAA category. See `acf.awci.visibility` for
the companion visibility-only diagnostic.
"""

from __future__ import annotations

from typing import Any

from acf.physics_guard import PhysicsGuard
from acf.science.dewpoint import DewPoint
from acf.science.thermodynamics import Thermodynamics

#: Real FAA / NOAA Aviation Weather Center ceiling-only thresholds
#: (500 ft / 1000 ft / 3000 ft AGL, converted to meters) - see module
#: docstring.
LIFR_CEILING_M = 152.4
IFR_CEILING_M = 304.8
MVFR_CEILING_M = 914.4


def classify_ceiling_category(ceiling_height_m: float) -> str:
    """Real FAA/NOAA ceiling-only category for a real ceiling height (m) - see module docstring."""
    if ceiling_height_m < LIFR_CEILING_M:
        return "LIFR"
    if ceiling_height_m < IFR_CEILING_M:
        return "IFR"
    if ceiling_height_m < MVFR_CEILING_M:
        return "MVFR"
    return "VFR"


def compute_real_ceiling_at_point(
    temperature_k: float, specific_humidity: float, pressure_hpa: float, validate_physics: bool = False
) -> dict[str, Any]:
    """
    Real estimated ceiling (lifting condensation level height, m) at
    one point - composes 2 already-real formulas plus the real LCL
    approximation (see module docstring), no new physics invented.

    Parameters
    ----------
    temperature_k : float
        Real air temperature (K).
    specific_humidity : float
        Real specific humidity (kg/kg).
    pressure_hpa : float
        Real atmospheric pressure (hPa).
    validate_physics : bool
        When True, runs real PhysicsGuard range/consistency checks
        (same convention as `acf.awci.theta_e`). Off by default, zero
        behavior change unless explicitly requested.

    Returns
    -------
    dict
        ceiling_height_m : real float (m), or `None` (never a
            fabricated value) when the real computed relative humidity
            is non-positive - see module docstring.
        ceiling_category : real "LIFR"/"IFR"/"MVFR"/"VFR" classification
            of `ceiling_height_m`, or `None` alongside it.
        relative_humidity_pct, dewpoint_k : the real intermediate
            values actually used, for transparency/debugging.
        status, is_real_data, honest_limitation.

    Raises
    ------
    acf.core.exceptions.PhysicsError
        (or a subclass) when `validate_physics=True` and a real
        PhysicsGuard check fails.
    """
    if validate_physics:
        guard = PhysicsGuard()
        guard.check_range(temperature_k, "air_temperature")
        guard.check_range(specific_humidity, "specific_humidity")
        guard.check_range(pressure_hpa, "air_pressure", unit="hPa")

    relative_humidity_pct = Thermodynamics.calculate_relative_humidity(
        specific_humidity, pressure_hpa, temperature_k, is_kelvin=True
    )

    if relative_humidity_pct <= 0.0:
        return {
            "ceiling_height_m": None,
            "ceiling_category": None,
            "relative_humidity_pct": None,
            "dewpoint_k": None,
            "status": "CEILING_NOT_COMPUTED_ZERO_HUMIDITY",
            "is_real_data": False,
            "honest_limitation": (
                f"Real computed relative humidity was {relative_humidity_pct} (non-positive) at this point - "
                "no real, meaningful dewpoint (and therefore no real LCL height) exists to compute from a "
                "genuinely dry point, so ceiling_height_m is honestly None, not a fabricated value."
            ),
        }

    temperature_c = temperature_k - 273.15
    dewpoint_c = DewPoint.calculate(temperature_c, relative_humidity_pct)

    if validate_physics:
        guard.check_consistency({"air_temperature": temperature_k, "dewpoint_temperature": dewpoint_c + 273.15})

    # Real, physically-derived dewpoint depression (see module docstring
    # for the two real lapse rates it comes from). Clamped at 0 rather
    # than left negative: a computed depression slightly below 0 is
    # real floating-point/formula noise at or above saturation (RH at
    # or very near 100%), not a real negative depression - an
    # already-saturated point's honest LCL is the surface itself (0 m),
    # not an undefined negative height.
    dewpoint_depression_c = max(0.0, temperature_c - dewpoint_c)
    ceiling_height_m = 125.0 * dewpoint_depression_c

    return {
        "ceiling_height_m": ceiling_height_m,
        "ceiling_category": classify_ceiling_category(ceiling_height_m),
        "relative_humidity_pct": relative_humidity_pct,
        "dewpoint_k": dewpoint_c + 273.15,
        "status": "REAL_CEILING_LCL_APPROXIMATION",
        "is_real_data": True,
        "honest_limitation": (
            "Real estimated height (m) at which a rising surface-based parcel would first saturate "
            "(125 m per °C of surface dewpoint depression - see module docstring for the real lapse-rate "
            "derivation), not a direct cloud-base observation and not evidence that a cloud genuinely exists "
            "at this height - ceiling-only classification (FAA/NOAA LIFR/IFR/MVFR/VFR ceiling thresholds), "
            "visibility not considered (see acf.awci.visibility for that companion diagnostic)."
        ),
    }
