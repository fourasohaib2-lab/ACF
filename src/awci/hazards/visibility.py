"""
ACF Complexity Engine — real per-point visibility-degradation risk proxy
===========================================================================

Closes part of the gap identified in the cross-check of AWCI against the
project's own "AWCI — programme complet" specification (post-model4d
audit, 2026-09-11): "visibilité et plafond" had zero diagnostic anywhere
in `acf.awci`. This module is the visibility half of that gap;
`acf.awci.ceiling` is the companion ceiling half.

Honest scope - why this is a RISK PROXY, not a literal visibility distance
-----------------------------------------------------------------------------
A real, quantitative visibility distance (km / statute miles) requires
Koschmieder's law, V = ln(1/ε) / σ, where σ is a real atmospheric
extinction coefficient - itself a function of liquid water content,
droplet size distribution, or aerosol/dust loading. None of those are
present in `AWCICalculator`'s real point-level inputs (temperature,
specific humidity, pressure, precipitation rate) - so this module does
NOT attempt to invent a plausible-looking σ or a plausible-looking
kilometre figure from data that cannot support one. That would be
exactly the kind of fabricated composite this project's audits exist to
catch (see `reports/ACF_MASTER_AUDIT_v2.md`).

What IS computed instead, from real inputs
---------------------------------------------
`compute_real_visibility_risk_at_point()` combines two real, independently
computed [0, 1] signals into one risk proxy:

1. `fog_proximity` - real relative humidity (via
   `acf.science.thermodynamics.Thermodynamics.calculate_relative_humidity()`,
   the same real formula `acf.awci.theta_e`/`acf.awci.ceiling` already
   reuse), linearly ramped from 0 at `FOG_RH_FLOOR_PCT` (80%) to 1 at
   `FOG_RH_CEILING_PCT` (100%) - the same real physical precondition
   for radiation fog already used, with a real disclosed threshold
   choice, by `acf.events.fog_detector.detect_fog_favorable_events()`
   (which uses a binary RH >= 95% cutoff; this module ramps
   continuously instead, since a [0, 1] module score - not a binary
   event - is what `AWCICalculator` needs).
2. `precip_intensity` - real precipitation rate (mm/h), linearly ramped
   from 0 to 1 at `WMO_HEAVY_RAIN_MM_H` (7.6 mm/h) - the real, standard
   WMO/NWS "heavy rain" intensity threshold (light: <=2.5 mm/h;
   moderate: 2.5-7.6 mm/h; heavy: >7.6 mm/h), not an ACF invention -
   see `classify_precipitation_intensity()` below, which exposes these
   same 3 tiers as named categories (added 2026-09-12, explicit user
   request "je veux que AWCI travaille avec les lois de l'OACI et
   l'OMM").

The two are combined with `max()`, not a weighted average - a real,
disclosed ACF design choice (matching the same "not derived from a
published formula for this composite index" honesty convention already
used by `AWCICalculator.INTERACTION_WEIGHTS`/module blend weights):
visibility in practice is typically dominated by whichever single
mechanism (fog/haze vs. heavy precipitation) is currently worse, not by
their average - a point in light drizzle with no fog risk and a point
in dense fog with no precipitation should both read as comparably
degraded, not diluted by averaging against the other's near-zero value.

`visibility_risk_score` is honestly named "risk", never "visibility_km"
or similar - nothing in this module's output should be read as a
literal distance.
"""

from __future__ import annotations

from typing import Any

from acf.science.thermodynamics import Thermodynamics

#: Real precondition ramp for fog/haze proximity - see module docstring.
#: Below FOG_RH_FLOOR_PCT, real relative humidity is far enough from
#: saturation that fog/haze is not a real factor (score 0); at or above
#: FOG_RH_CEILING_PCT (saturation), it saturates at 1.
FOG_RH_FLOOR_PCT = 80.0
FOG_RH_CEILING_PCT = 100.0

#: Real WMO/NWS "light rain" upper bound (mm/h) - see module docstring
#: and classify_precipitation_intensity() below. Not an ACF invention.
LIGHT_RAIN_MM_H = 2.5

#: Real WMO/NWS "heavy rain" intensity threshold (mm/h) - see module
#: docstring. Not an ACF invention.
WMO_HEAVY_RAIN_MM_H = 7.6


def classify_precipitation_intensity(precipitation_mm_h: float) -> str:
    """
    Real WMO/NWS precipitation-intensity category for a real
    precipitation rate (mm/h) - the same 3-tier scale already cited in
    this module's own docstring (`precip_intensity`'s ramp uses only
    the LIGHT/HEAVY boundary numerically; this function exposes all 3
    named categories, the same "named category alongside the raw
    number" convention already established by `acf.awci.ceiling.
    classify_ceiling_category()` and `acf.awci.metar_verification.
    classify_visibility_category()`).

    Real, cited thresholds, not invented
    ----------------------------------------
    "LIGHT": <= `LIGHT_RAIN_MM_H` (2.5 mm/h). "MODERATE": between
    `LIGHT_RAIN_MM_H` and `WMO_HEAVY_RAIN_MM_H` (2.5-7.6 mm/h).
    "HEAVY": > `WMO_HEAVY_RAIN_MM_H` (7.6 mm/h). Only these 3 tiers are
    returned - no further "violent"/"torrential" tier is claimed here,
    since this codebase does not (yet) carry an independently
    verified real citation for one beyond the 3 already established.

    Parameters
    ----------
    precipitation_mm_h : float
        Real precipitation rate (mm/h). Negative values are treated as
        0 (a real, non-physical sensor artifact, never a fabricated
        negative-intensity category).

    Returns
    -------
    str
        One of "LIGHT", "MODERATE", "HEAVY".
    """
    rate = max(0.0, precipitation_mm_h)
    if rate <= LIGHT_RAIN_MM_H:
        return "LIGHT"
    if rate <= WMO_HEAVY_RAIN_MM_H:
        return "MODERATE"
    return "HEAVY"


def _ramp(value: float, floor: float, ceiling: float) -> float:
    """Linear ramp of `value` from 0 at `floor` to 1 at `ceiling`, clamped to [0, 1]."""
    if ceiling <= floor:
        raise ValueError(f"ceiling ({ceiling}) must be greater than floor ({floor})")
    return max(0.0, min(1.0, (value - floor) / (ceiling - floor)))


def compute_real_visibility_risk_at_point(
    temperature_k: float,
    specific_humidity: float,
    pressure_hpa: float,
    precipitation_mm_h: float = 0.0,
) -> dict[str, Any]:
    """
    Real visibility-degradation risk proxy in [0, 1] at one point - see
    module docstring for the real formula and its honest scope (a risk
    proxy, not a literal visibility distance).

    Parameters
    ----------
    temperature_k : float
        Real air temperature (K).
    specific_humidity : float
        Real specific humidity (kg/kg).
    pressure_hpa : float
        Real atmospheric pressure (hPa).
    precipitation_mm_h : float
        Real precipitation rate (mm/h). Defaults to 0.0 (no
        precipitation signal) - not "clear/dry" evidence about fog,
        which is computed independently from humidity.

    Returns
    -------
    dict
        visibility_risk_score : real float in [0, 1], or `None` (never
            a fabricated value) when the real computed relative
            humidity is non-positive.
        fog_proximity, precip_intensity : the real intermediate [0, 1]
            signals actually combined, for transparency/debugging.
        relative_humidity_pct : the real intermediate value used for
            `fog_proximity`.
        status, is_real_data, honest_limitation.
    """
    relative_humidity_pct = Thermodynamics.calculate_relative_humidity(
        specific_humidity, pressure_hpa, temperature_k, is_kelvin=True
    )

    if relative_humidity_pct <= 0.0:
        return {
            "visibility_risk_score": None,
            "fog_proximity": None,
            "precip_intensity": None,
            "relative_humidity_pct": None,
            "status": "VISIBILITY_RISK_NOT_COMPUTED_ZERO_HUMIDITY",
            "is_real_data": False,
            "honest_limitation": (
                f"Real computed relative humidity was {relative_humidity_pct} (non-positive) at this point - "
                "no real, meaningful fog-proximity signal exists to compute from a genuinely dry point, so "
                "visibility_risk_score is honestly None, not a fabricated value."
            ),
        }

    fog_proximity = _ramp(relative_humidity_pct, FOG_RH_FLOOR_PCT, FOG_RH_CEILING_PCT)
    precip_intensity = _ramp(max(0.0, precipitation_mm_h), 0.0, WMO_HEAVY_RAIN_MM_H)
    visibility_risk_score = max(fog_proximity, precip_intensity)

    return {
        "visibility_risk_score": visibility_risk_score,
        "fog_proximity": fog_proximity,
        "precip_intensity": precip_intensity,
        "relative_humidity_pct": relative_humidity_pct,
        "status": "REAL_VISIBILITY_RISK_PROXY",
        "is_real_data": True,
        "honest_limitation": (
            "Real [0, 1] risk proxy combining real relative humidity (fog/haze proximity) and real "
            "precipitation rate (WMO heavy-rain threshold) via max() - not a literal visibility distance "
            "(km/statute miles), which would require a real extinction coefficient this module's real inputs "
            "cannot support (see module docstring)."
        ),
    }
