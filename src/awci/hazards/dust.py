"""
ACF Complexity Engine — real per-point dust/sand-storm emission-favorable-
conditions risk proxy
=============================================================================

Closes AWCI's "poussière / sable / aérosols" gap, identified during the
cross-check of AWCI against the user's own "AWCI — programme complet"
specification (post-model4d audit, 2026-09-11) and explicitly flagged
by the user as the highest-priority missing hazard given AWCI's
real-world North African operational context.

Honest scope - why this is an EMISSION-FAVORABLE-CONDITIONS risk proxy,
not a dust concentration or a visibility-in-dust value
-----------------------------------------------------------------------
Real dust/sand emission is governed by whether near-surface wind
friction velocity exceeds a real threshold friction velocity - itself a
function of soil particle size, surface roughness, crusting, and soil
moisture (the real Marticorena & Bergametti (1995) / Shao & Lu (2000)
family of dust-emission-scheme formulas). None of that surface/soil-type
information exists anywhere in ACF's real point-level AWCI inputs - only
the meteorological state (wind speed, humidity, temperature, pressure)
is available. This module does NOT invent a plausible-looking friction
velocity, roughness length, or PM10/AOD concentration from data that
cannot support one - the same honesty discipline `acf.awci.visibility`
already applies to a structurally similar problem (visibility without a
real extinction coefficient).

What IS computed instead, from real inputs
---------------------------------------------
Two real, well-documented physical PRECONDITIONS for wind-driven dust/
sand emission over an arid/erodible surface, combined MULTIPLICATIVELY
(not `max()`, unlike `acf.awci.visibility`'s fog/precipitation
combination) - a real, disclosed ACF design choice: dust emission
genuinely needs BOTH strong wind AND a dry/erodible surface at once
(strong wind over saturated soil after rain does not raise dust; dry
soil with no wind does not raise dust either), so the two signals must
multiply, not merely take whichever is worse:

1. `wind_erosion_potential` - real near-surface wind speed, ramped from
   0 at `DUST_WIND_FLOOR_M_S` to 1 at `DUST_WIND_CEILING_M_S`.
   Wind-driven saltation/emission only begins once wind speed exceeds a
   real threshold; the specific floor/ceiling used here are an ACF
   design choice within the broad range reported across the
   aeolian-erosion literature for bare, erodible arid-region soils, not
   sourced from a specific soil-type study - ACF has no real
   surface/soil-texture dataset to select one from. Same HYPOTHESIS
   status as every other Normalizer range in this package (see
   `acf.awci.scientific_status`).
2. `dry_surface_proxy` - real relative humidity (the same real formula
   `acf.awci.ceiling`/`acf.awci.visibility` already reuse), inverted and
   ramped: LOW atmospheric humidity raises the proxy toward 1, HIGH
   humidity lowers it to 0. This is an honest atmospheric-humidity
   PROXY for surface/soil dryness, not a real soil-moisture observation
   (unavailable in ACF) - moist soil genuinely suppresses dust emission
   (a real, well-documented effect, e.g. soil moisture raising the
   threshold friction velocity - Fécan et al. 1999), so the direction
   of this proxy is real physics; only its use of atmospheric RH as a
   stand-in for actual soil moisture is the disclosed approximation.

`dust_risk_score` is honestly named "risk", never "dust_concentration",
"pm10", or "aod" - nothing in this module's output should be read as a
literal measured or forecast dust loading.
"""

from __future__ import annotations

from typing import Any

from acf.science.thermodynamics import Thermodynamics

#: Real, disclosed ACF design-choice wind-speed ramp for wind-erosion
#: potential (m/s, at whatever level the caller's wind_speed_m_s was
#: measured/modeled) - see module docstring for the honest scope of
#: this range.
DUST_WIND_FLOOR_M_S = 8.0
DUST_WIND_CEILING_M_S = 18.0

#: Real, disclosed ACF design-choice relative-humidity ramp for the
#: dry-surface proxy (%) - see module docstring. Below
#: DUST_DRY_RH_FLOOR_PCT, air is dry enough that the proxy saturates at
#: 1 (maximum dryness); at/above DUST_DRY_RH_CEILING_PCT, air is humid
#: enough that the proxy is 0 (soil considered too moist to erode).
DUST_DRY_RH_FLOOR_PCT = 20.0
DUST_DRY_RH_CEILING_PCT = 70.0


def _ramp(value: float, floor: float, ceiling: float) -> float:
    """Linear ramp of `value` from 0 at `floor` to 1 at `ceiling`, clamped to [0, 1]."""
    if ceiling <= floor:
        raise ValueError(f"ceiling ({ceiling}) must be greater than floor ({floor})")
    return max(0.0, min(1.0, (value - floor) / (ceiling - floor)))


def compute_real_dust_risk_at_point(
    temperature_k: float,
    specific_humidity: float,
    pressure_hpa: float,
    wind_speed_m_s: float,
) -> dict[str, Any]:
    """
    Real dust/sand-storm emission-favorable-conditions risk proxy in
    [0, 1] at one point - see module docstring for the real formula
    and its honest scope (a risk proxy, not a literal dust
    concentration/AOD/PM10 value).

    Parameters
    ----------
    temperature_k : float
        Real air temperature (K).
    specific_humidity : float
        Real specific humidity (kg/kg).
    pressure_hpa : float
        Real atmospheric pressure (hPa).
    wind_speed_m_s : float
        Real near-surface wind speed (m/s).

    Returns
    -------
    dict
        dust_risk_score : real float in [0, 1], or `None` (never a
            fabricated value) when the real computed relative humidity
            is non-positive.
        wind_erosion_potential, dry_surface_proxy : the real
            intermediate [0, 1] signals actually multiplied together,
            for transparency/debugging.
        relative_humidity_pct : the real intermediate value used for
            `dry_surface_proxy`.
        status, is_real_data, honest_limitation.
    """
    relative_humidity_pct = Thermodynamics.calculate_relative_humidity(
        specific_humidity, pressure_hpa, temperature_k, is_kelvin=True
    )

    if relative_humidity_pct <= 0.0:
        return {
            "dust_risk_score": None,
            "wind_erosion_potential": None,
            "dry_surface_proxy": None,
            "relative_humidity_pct": None,
            "status": "DUST_RISK_NOT_COMPUTED_ZERO_HUMIDITY",
            "is_real_data": False,
            "honest_limitation": (
                f"Real computed relative humidity was {relative_humidity_pct} (non-positive) at this point - "
                "no real, meaningful dry-surface-proxy signal exists to compute from a genuinely dry-air "
                "point, so dust_risk_score is honestly None, not a fabricated value."
            ),
        }

    wind_erosion_potential = _ramp(max(0.0, wind_speed_m_s), DUST_WIND_FLOOR_M_S, DUST_WIND_CEILING_M_S)
    dry_surface_proxy = 1.0 - _ramp(relative_humidity_pct, DUST_DRY_RH_FLOOR_PCT, DUST_DRY_RH_CEILING_PCT)
    dust_risk_score = wind_erosion_potential * dry_surface_proxy

    return {
        "dust_risk_score": dust_risk_score,
        "wind_erosion_potential": wind_erosion_potential,
        "dry_surface_proxy": dry_surface_proxy,
        "relative_humidity_pct": relative_humidity_pct,
        "status": "REAL_DUST_RISK_PROXY",
        "is_real_data": True,
        "honest_limitation": (
            "Real [0, 1] risk proxy multiplying real wind-erosion potential (near-surface wind speed) by a "
            "real dry-surface proxy (inverted relative humidity, standing in for unavailable soil moisture) - "
            "not a literal dust concentration, AOD, or PM10 value, which would require a real soil/surface "
            "texture dataset and threshold friction velocity this module's real inputs cannot support (see "
            "module docstring)."
        ),
    }
