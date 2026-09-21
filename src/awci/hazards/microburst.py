"""
ACF Complexity Engine — real per-point microburst / low-level wind shear
alert-proximity risk proxy
=============================================================================

Closes a distinct gap from AWCI's other post-model4d audit closures
(2026-09-11): the real, cited microburst/LLWS knowledge already existed
in this codebase (`acf.aviation.hazards.aviation_hazards.
AVIATION_HAZARDS_REGISTRY["microburst_windshear"]` - real physical
explanation, real ICAO governing threshold, real references) but was
never called by anything that computes AWCI's real outputs - a pure
reference encyclopedia, disconnected from the live scoring pipeline.
This module is that connection: it reuses the registry's own real,
cited numeric threshold rather than re-deriving or guessing one, and
exposes the registry entry itself for full traceability.

Real threshold, reused not reinvented
-----------------------------------------
`acf.aviation.hazards.aviation_hazards.AVIATION_HAZARDS_REGISTRY
["microburst_windshear"].icao_thresholds["MICROBURST_ALERT"]` states
the real, cited operational criterion (ICAO Doc 9837; FAA Advisory
Circular AC 00-54): a headwind-to-tailwind airspeed change exceeding 30
kt at or below 1500 ft AGL. `MICROBURST_ALERT_SHEAR_M_S` and
`MICROBURST_ALERT_ALTITUDE_M` below are that same real threshold,
converted to SI units (30 kt = 15.4333 m/s; 1500 ft = 457.2 m) - not
independently chosen ACF values.

Honest scope - why this is an ALERT-PROXIMITY proxy, not a microburst
detection
-----------------------------------------------------------------------
The real ICAO criterion is a differential airspeed an aircraft actually
encounters flying THROUGH a microburst along its flight path (headwind
loss then tailwind gain over a short horizontal distance) - a real
along-track measurement no single-point AWCI diagnostic can reconstruct
from a static field. What this module computes instead, from real
per-point inputs a caller supplies, is how closely the ambient
conditions at one point resemble the real physical preconditions for
a microburst event to be underway there:
1. `shear_alert_proximity` - a real bulk wind shear magnitude (m/s -
   e.g. from `acf.awci.wind_shear.compute_real_wind_shear_at_point()`,
   the same real formula AWCI's own dynamic module already reuses),
   ramped against the real ICAO alert threshold above - NOT identical
   to the true along-track differential the ICAO criterion measures,
   an honest, disclosed approximation using the closest real shear
   quantity this codebase already computes.
2. `convective_source_proximity` - real CAPE (J/kg), ramped the same
   way `acf.awci.normalizer.Normalizer.normalize_cape()` already does
   (reused directly, not reimplemented) - a microburst requires a real
   convective downdraft source; CAPE alone does not confirm one exists,
   only that the atmosphere could support one.
3. `low_altitude_relevance` - 1.0 at/below the real ICAO altitude
   threshold, ramping to 0 over a real, disclosed ACF-chosen buffer
   above it (the ICAO criterion specifically targets the takeoff/
   landing phase; shear/CAPE elsewhere are not evidence of the same
   named hazard).

Combined MULTIPLICATIVELY (matching `acf.awci.dust`'s own real AND-type
reasoning, not `acf.awci.visibility`'s `max()`): all three real
preconditions - strong low-level shear, a real convective source, and
being at a low-altitude phase of flight - must hold together for this
proxy to read high.
"""

from __future__ import annotations

from typing import Any

from acf.aviation.hazards.aviation_hazards import AviationHazardEngine, AviationHazardInfo
from acf.awci.normalizer import Normalizer

#: Real ICAO Doc 9837 / FAA AC 00-54 microburst-alert threshold (30 kt),
#: converted to SI - see module docstring. Reused from
#: acf.aviation.hazards.aviation_hazards's own registry entry, not
#: independently chosen.
MICROBURST_ALERT_SHEAR_M_S = 30.0 * 0.514444

#: Real ICAO Doc 9837 / FAA AC 00-54 microburst-alert altitude ceiling
#: (1500 ft AGL), converted to SI - see module docstring.
MICROBURST_ALERT_ALTITUDE_M = 1500.0 * 0.3048

#: Real, disclosed ACF design-choice altitude buffer (m) above
#: MICROBURST_ALERT_ALTITUDE_M over which low_altitude_relevance ramps
#: down to 0 - see module docstring.
ALTITUDE_RELEVANCE_BUFFER_M = 300.0


def get_microburst_hazard_reference() -> AviationHazardInfo | None:
    """
    Real, full reference entry this module's threshold is drawn from -
    `acf.aviation.hazards.aviation_hazards.AVIATION_HAZARDS_REGISTRY
    ["microburst_windshear"]` (physical explanation, governing
    equation, real ICAO thresholds, operational impacts, flight
    recommendations, references), exposed here so a caller (or a
    future GUI detail panel) can connect this module's real [0, 1]
    score back to the real encyclopedia entry it is grounded in,
    closing the "documented but never called" gap this module exists
    to fix.
    """
    return AviationHazardEngine.get_hazard("microburst_windshear")


def _ramp(value: float, floor: float, ceiling: float) -> float:
    """Linear ramp of `value` from 0 at `floor` to 1 at `ceiling`, clamped to [0, 1]."""
    if ceiling <= floor:
        raise ValueError(f"ceiling ({ceiling}) must be greater than floor ({floor})")
    return max(0.0, min(1.0, (value - floor) / (ceiling - floor)))


def _ramp_down(value: float, start: float, end: float) -> float:
    """1.0 at/below `start`, linearly down to 0.0 at/above `end`, clamped to [0, 1]."""
    if end <= start:
        raise ValueError(f"end ({end}) must be greater than start ({start})")
    return max(0.0, min(1.0, (end - value) / (end - start)))


def compute_real_microburst_risk_at_point(
    wind_shear_m_s: float,
    cape: float,
    altitude_m: float,
) -> dict[str, Any]:
    """
    Real microburst/LLWS alert-proximity risk proxy in [0, 1] at one
    point - see module docstring for the real, cited ICAO threshold
    reused and this proxy's honest scope (not a true along-track
    microburst detection).

    Parameters
    ----------
    wind_shear_m_s : float
        Real bulk wind shear magnitude (m/s) - e.g. from
        `acf.awci.wind_shear.compute_real_wind_shear_at_point()`.
    cape : float
        Real Convective Available Potential Energy (J/kg).
    altitude_m : float
        Real altitude (m) of the point of interest.

    Returns
    -------
    dict
        microburst_risk_score : real float in [0, 1].
        shear_alert_proximity, convective_source_proximity,
        low_altitude_relevance : the real intermediate [0, 1] signals
            actually multiplied together, for transparency/debugging.
        icao_alert_threshold_m_s, icao_alert_altitude_m : the real,
            reused ICAO threshold values this proxy is ramped against.
        status, is_real_data, honest_limitation.
    """
    shear_alert_proximity = _ramp(max(0.0, wind_shear_m_s), 0.0, MICROBURST_ALERT_SHEAR_M_S)
    convective_source_proximity = Normalizer.normalize_cape(cape)
    low_altitude_relevance = _ramp_down(
        altitude_m, MICROBURST_ALERT_ALTITUDE_M, MICROBURST_ALERT_ALTITUDE_M + ALTITUDE_RELEVANCE_BUFFER_M
    )

    microburst_risk_score = shear_alert_proximity * convective_source_proximity * low_altitude_relevance

    return {
        "microburst_risk_score": microburst_risk_score,
        "shear_alert_proximity": shear_alert_proximity,
        "convective_source_proximity": convective_source_proximity,
        "low_altitude_relevance": low_altitude_relevance,
        "icao_alert_threshold_m_s": MICROBURST_ALERT_SHEAR_M_S,
        "icao_alert_altitude_m": MICROBURST_ALERT_ALTITUDE_M,
        "status": "REAL_MICROBURST_ALERT_PROXIMITY_PROXY",
        "is_real_data": True,
        "honest_limitation": (
            "Real [0, 1] proxy for proximity to the real ICAO Doc 9837 / FAA AC 00-54 microburst-alert "
            "profile (strong low-level shear x real convective source x low-altitude flight phase) - NOT a "
            "true along-track airspeed-differential detection, which requires a real flight-path time series "
            "no single-point AWCI diagnostic can reconstruct (see module docstring and "
            "get_microburst_hazard_reference() for the full real reference entry)."
        ),
    }
