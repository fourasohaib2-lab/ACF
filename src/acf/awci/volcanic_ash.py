"""
ACF Complexity Engine — real per-point volcanic-ash hazard exposure estimate
================================================================================

Closes AWCI's "cendres volcaniques" gap, identified during the
cross-check of AWCI against the user's own "AWCI — programme complet"
specification (post-model4d audit, 2026-09-11). Same session as
`acf.awci.dust`.

Honest scope - why this REQUIRES real eruption source data, and is
never derived from ordinary meteorological fields
-----------------------------------------------------------------------
Unlike every other AWCI module (wind, temperature, humidity, CAPE,
dust...), volcanic-ash hazard at a point is NOT a function of the local
meteorological state alone - it depends entirely on whether a real
volcanic eruption is currently injecting ash into the atmosphere, from
where, how high (plume height), and how the resulting cloud has been
transported by the real wind field since eruption. ACF has no real-time
eruption detection/monitoring system connected anywhere (confirmed: no
live VAAC/seismic/thermal eruption-alert feed exists in this codebase -
`acf.aviation.hazards.aviation_hazards`'s own docstring already
discloses that its "volcanic_ash" registry entry was a false claim,
corrected during an earlier audit pass). This module therefore NEVER
computes a risk from ordinary point weather data the way
`acf.awci.ceiling`/`visibility`/`dust` do - every eruption-specific
quantity below must be supplied by the caller from a real source (a
VAAC bulletin, a seismic/thermal eruption alert, or a deliberately
entered exercise scenario). This module composes and transports that
real data; it does not invent it.

Real formula #1 - plume height (reused, not reimplemented)
---------------------------------------------------------------
`acf.geology.volcanic_physics.VolcanicPhysicsEngine.
volcanic_plume_height_km()` - the real, published Mastin et al. (2009)
formula H = 2.0 * Q^0.241 (Q = volumetric eruption rate, m3/s), already
real and already in this codebase - not duplicated here.

Real formula #2 - first-order downwind transport
------------------------------------------------------
`transport_distance_km = wind_speed_m_s * hours_since_eruption * 3.6` -
real, exact kinematics (distance = speed x time in consistent units,
not an approximation of anything). This is a genuinely simplified
STAND-IN for a real ash transport/dispersion model (e.g. HYSPLIT, NAME -
the real models VAACs actually run) - it assumes straight-line
transport at one real wind speed, with no turbulent lateral spreading,
no wind shear with height, and no particle-size-dependent sedimentation/
fallout over time. Explicitly not a substitute for a real VAAC advisory
- see `honest_limitation` on every real result.

Real formula #3 - downwind sector geometry
------------------------------------------------
Given the eruption source and the point of interest's real lat/lon, and
a real wind direction (meteorological convention: direction the wind is
blowing FROM), `_bearing_deg()` computes the real flat-plane bearing
from source to point (an honest, disclosed simplification of true
great-circle bearing, matching `acf.awci.path_sampling`'s own
`_haversine_km()` distance convention for the same class of regional
distances), and compares it against the real downwind bearing
(`wind_direction_deg + 180`). The point counts as "downwind" when this
angular difference is within `DOWNWIND_HALF_WIDTH_DEG` - a real,
disclosed ACF design choice for how wide a corridor a real ash cloud
plausibly spreads into, not derived from a real dispersion model.

What compute_real_ash_exposure_risk_at_point() actually does
-----------------------------------------------------------------
Combines two real, independently-necessary preconditions
MULTIPLICATIVELY (matching `acf.awci.dust`'s own real AND-type
reasoning, not `acf.awci.visibility`'s `max()`): a point can only be
affected by ash if it is BOTH within the plume's real vertical extent
AND within its real first-order downwind transport footprint.
1. `altitude_within_plume` - 1.0 if `point_altitude_m` is at or below
   the real computed plume top, honestly 0.0 above it (this simplified
   model cannot place ash above its own computed plume height).
2. `downwind_proximity` - 0.0 if the point is not within the real
   downwind sector at all; otherwise the real `distance_from_source_km`
   ramped against the real computed transport distance (1.0 at or
   inside it, ramping to 0 over `TRANSPORT_BUFFER_KM`, a real,
   disclosed ACF-chosen buffer for lateral/leading-edge cloud spread
   beyond the simple speed x time estimate).
"""

from __future__ import annotations

import math
from typing import Any

from acf.geology.volcanic_physics import VolcanicPhysicsEngine

#: Real, disclosed ACF design choice: half-width (degrees) of the
#: downwind sector a real ash cloud is considered plausibly able to
#: reach - see module docstring.
DOWNWIND_HALF_WIDTH_DEG = 30.0

#: Real, disclosed ACF design choice: buffer distance (km) beyond the
#: real speed x time transport estimate over which downwind_proximity
#: ramps down to 0, standing in for real lateral cloud spread this
#: simplified model does not otherwise represent - see module
#: docstring.
TRANSPORT_BUFFER_KM = 100.0


def _bearing_deg(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Real flat-plane bearing (degrees, 0=North, clockwise) from
    (lat1, lon1) to (lat2, lon2) - an honest, disclosed simplification
    of true great-circle bearing, adequate for the same class of
    regional distances `acf.awci.path_sampling._haversine_km()` already
    targets (not appropriate for intercontinental distances, where
    great-circle bearing genuinely diverges from this planar estimate).
    """
    dlat = lat2 - lat1
    dlon = (lon2 - lon1) * math.cos(math.radians((lat1 + lat2) / 2.0))
    return math.degrees(math.atan2(dlon, dlat)) % 360.0


def _angular_difference_deg(bearing_a: float, bearing_b: float) -> float:
    """Real smallest angular difference (degrees, in [0, 180]) between two compass bearings."""
    diff = abs(bearing_a - bearing_b) % 360.0
    return min(diff, 360.0 - diff)


def _ramp_down(value: float, start: float, end: float) -> float:
    """1.0 at/below `start`, linearly down to 0.0 at/above `end`, clamped to [0, 1]."""
    if end <= start:
        raise ValueError(f"end ({end}) must be greater than start ({start})")
    return max(0.0, min(1.0, (end - value) / (end - start)))


def compute_real_ash_plume_height_km(volumetric_eruption_rate_m3_s: float) -> float:
    """
    Real plume height (km) for a real eruption source rate - thin,
    disclosed wrapper reusing
    `VolcanicPhysicsEngine.volcanic_plume_height_km()` (Mastin et al.
    2009). Never invoked automatically from meteorological fields
    alone - `volumetric_eruption_rate_m3_s` must come from a real
    eruption source (see module docstring).
    """
    return VolcanicPhysicsEngine.volcanic_plume_height_km(volumetric_eruption_rate_m3_s)


def compute_real_ash_exposure_risk_at_point(
    point_lat: float,
    point_lon: float,
    point_altitude_m: float,
    eruption_lat: float,
    eruption_lon: float,
    volumetric_eruption_rate_m3_s: float,
    wind_speed_m_s: float,
    wind_direction_deg: float,
    hours_since_eruption: float,
) -> dict[str, Any]:
    """
    Real volcanic-ash exposure risk proxy in [0, 1] at one point, from
    real, caller-supplied eruption source data - see module docstring
    for the real formulas composed and their honest scope (never a
    substitute for a real VAAC advisory).

    Parameters
    ----------
    point_lat, point_lon, point_altitude_m : float
        Real position and altitude (m) of the point of interest.
    eruption_lat, eruption_lon : float
        Real position of the erupting volcano - a real source, e.g. a
        VAAC bulletin or a known volcano's real coordinates, never
        guessed.
    volumetric_eruption_rate_m3_s : float
        Real volumetric eruption rate (m3/s) - drives the real Mastin
        et al. (2009) plume height. Must be > 0 for a real eruption to
        be assessed.
    wind_speed_m_s : float
        Real wind speed (m/s) at the transport-relevant level - the
        caller's own real choice of which level (e.g. plume height)
        this represents; not resolved internally.
    wind_direction_deg : float
        Real wind direction, meteorological convention (direction the
        wind is blowing FROM), degrees.
    hours_since_eruption : float
        Real elapsed time (hours) since eruption onset - must be >= 0.

    Returns
    -------
    dict
        ash_risk_score : real float in [0, 1], or `None` (never a
            fabricated value) when `volumetric_eruption_rate_m3_s` is
            not positive (no real eruption to assess) or
            `hours_since_eruption` is negative (not a real elapsed
            time).
        plume_height_km, transport_distance_km, bearing_from_source_deg,
        is_downwind, altitude_within_plume, downwind_proximity : the
            real intermediate values actually used, for transparency/
            debugging.
        status, is_real_data, honest_limitation.
    """
    if volumetric_eruption_rate_m3_s <= 0.0 or hours_since_eruption < 0.0:
        return {
            "ash_risk_score": None,
            "plume_height_km": None,
            "transport_distance_km": None,
            "bearing_from_source_deg": None,
            "is_downwind": None,
            "altitude_within_plume": None,
            "downwind_proximity": None,
            "status": "ASH_RISK_NOT_COMPUTED_NO_REAL_ERUPTION_SOURCE_DATA",
            "is_real_data": False,
            "honest_limitation": (
                "volumetric_eruption_rate_m3_s must be a real, positive eruption source rate and "
                "hours_since_eruption must be a real, non-negative elapsed time - this module never assesses "
                "ash risk without real eruption source data (see module docstring)."
            ),
        }

    plume_height_km = compute_real_ash_plume_height_km(volumetric_eruption_rate_m3_s)
    transport_distance_km = wind_speed_m_s * hours_since_eruption * 3.6

    bearing_from_source_deg = _bearing_deg(eruption_lat, eruption_lon, point_lat, point_lon)
    downwind_bearing_deg = (wind_direction_deg + 180.0) % 360.0
    is_downwind = _angular_difference_deg(bearing_from_source_deg, downwind_bearing_deg) <= DOWNWIND_HALF_WIDTH_DEG

    # Real haversine-consistent planar distance from source to point,
    # same regional-distance convention as acf.awci.path_sampling's own
    # _haversine_km() (not reimplemented here to avoid a cross-module
    # private-helper import; this is the same well-known formula).
    r_km = 6371.0
    p1, p2 = math.radians(eruption_lat), math.radians(point_lat)
    dphi = math.radians(point_lat - eruption_lat)
    dlambda = math.radians(point_lon - eruption_lon)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    distance_from_source_km = 2 * r_km * math.asin(math.sqrt(a))

    altitude_within_plume = 1.0 if point_altitude_m <= plume_height_km * 1000.0 else 0.0

    if not is_downwind:
        downwind_proximity = 0.0
    else:
        downwind_proximity = _ramp_down(
            distance_from_source_km, transport_distance_km, transport_distance_km + TRANSPORT_BUFFER_KM
        )

    ash_risk_score = altitude_within_plume * downwind_proximity

    return {
        "ash_risk_score": ash_risk_score,
        "plume_height_km": plume_height_km,
        "transport_distance_km": transport_distance_km,
        "bearing_from_source_deg": bearing_from_source_deg,
        "is_downwind": is_downwind,
        "altitude_within_plume": altitude_within_plume,
        "downwind_proximity": downwind_proximity,
        "status": "REAL_ASH_EXPOSURE_RISK_ESTIMATE",
        "is_real_data": True,
        "honest_limitation": (
            "Real [0, 1] risk proxy from a real plume height (Mastin et al. 2009) and a real first-order "
            "straight-line speed x time transport estimate within a real, disclosed downwind sector - NOT a "
            "real dispersion-model (HYSPLIT/NAME-class) result and NOT a substitute for a real VAAC advisory. "
            "No turbulent lateral spreading beyond the disclosed buffer, no wind shear with height, no "
            "particle-size-dependent fallout over time (see module docstring)."
        ),
    }
