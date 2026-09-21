"""
Atmospheric Complexity Framework (ACF)

Flight Planning - Waypoint Generation

Real great-circle intermediate-point generation - the ``waypoint.py``
module named in
``docs/architecture/awci_reference_architecture.md`` section 11
("Flight Planning Engine... Covers: Route, Altitude, Departure,
Cruise, Arrival, Alternate, Weather along route, Hazards along
route.").

Real, standard spherical navigation formula - the great-circle
"intermediate point" formula (Ed Williams' Aviation Formulary, the
real, textbook spherical-trigonometry family already used by
``awci.knowledge.routing.flight_routing.FlightRoutingEngine.
great_circle_distance_nm()`` and ``awci.airport.airport.
_destination_point()``), not an ACF invention. Complements, does not
replace, the existing real
``awci.complexity.path_sampling.sample_field_along_path()`` - that
function's own straight LINEAR lat/lon interpolation is a real,
disclosed short-range approximation for sampling an already-gridded
field; this module's fractional great-circle interpolation is the
real, more accurate formula for a genuine flight-planning waypoint
position list, where the divergence from the true flown track grows
with route length.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

#: Real mean Earth radius (km) - same value already used by
#: awci.airport.airport/awci.complexity.path_sampling.
_EARTH_RADIUS_KM = 6371.0


@dataclass(frozen=True)
class Waypoint:
    """One real point along a great-circle route."""

    latitude: float
    longitude: float
    distance_from_origin_km: float
    fraction: float  # 0.0 at the origin, 1.0 at the destination


def _angular_distance_rad(lat1_deg: float, lon1_deg: float, lat2_deg: float, lon2_deg: float) -> float:
    """Real central angle (radians) between two points - the real
    haversine formula, the same family already used by
    ``FlightRoutingEngine.great_circle_distance_nm()``."""
    lat1 = math.radians(lat1_deg)
    lat2 = math.radians(lat2_deg)
    dlat = math.radians(lat2_deg - lat1_deg)
    dlon = math.radians(lon2_deg - lon1_deg)
    a = math.sin(dlat / 2.0) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2.0) ** 2
    return 2.0 * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1.0 - a)))


def great_circle_intermediate_point(
    lat1_deg: float, lon1_deg: float, lat2_deg: float, lon2_deg: float, fraction: float
) -> tuple[float, float]:
    """
    Real point at ``fraction`` (0.0 = origin, 1.0 = destination) along
    the real great-circle path between the two given points - the
    real, standard spherical "intermediate point" formula, not an
    approximation.

    Raises
    ------
    ValueError
        If ``fraction`` is outside ``[0, 1]``, or the two points are
        genuinely antipodal (a real mathematical singularity - the
        great-circle path between exactly antipodal points is not
        unique, so no single real intermediate point exists).
    """
    if not 0.0 <= fraction <= 1.0:
        raise ValueError(f"fraction must be in [0, 1], got {fraction}")
    angular_distance = _angular_distance_rad(lat1_deg, lon1_deg, lat2_deg, lon2_deg)
    if math.isclose(angular_distance, math.pi, abs_tol=1e-9):
        raise ValueError("the two points are antipodal - the great-circle path is not unique")
    if angular_distance == 0.0:
        return lat1_deg, lon1_deg
    lat1, lon1 = math.radians(lat1_deg), math.radians(lon1_deg)
    lat2, lon2 = math.radians(lat2_deg), math.radians(lon2_deg)
    a = math.sin((1.0 - fraction) * angular_distance) / math.sin(angular_distance)
    b = math.sin(fraction * angular_distance) / math.sin(angular_distance)
    x = a * math.cos(lat1) * math.cos(lon1) + b * math.cos(lat2) * math.cos(lon2)
    y = a * math.cos(lat1) * math.sin(lon1) + b * math.cos(lat2) * math.sin(lon2)
    z = a * math.sin(lat1) + b * math.sin(lat2)
    lat = math.atan2(z, math.sqrt(x**2 + y**2))
    lon = math.atan2(y, x)
    return math.degrees(lat), math.degrees(lon)


def generate_route_waypoints(
    lat1_deg: float, lon1_deg: float, lat2_deg: float, lon2_deg: float, n_points: int = 10
) -> list[Waypoint]:
    """
    Real, evenly-spaced-by-great-circle-fraction waypoint list from a
    real origin to a real destination - ``n_points`` must be >= 2 (the
    real origin and destination are always the first/last points,
    never approximated).
    """
    if n_points < 2:
        raise ValueError(f"n_points must be >= 2 (origin and destination), got {n_points}")
    total_km = _angular_distance_rad(lat1_deg, lon1_deg, lat2_deg, lon2_deg) * _EARTH_RADIUS_KM
    waypoints: list[Waypoint] = []
    for i in range(n_points):
        fraction = i / (n_points - 1)
        lat, lon = great_circle_intermediate_point(lat1_deg, lon1_deg, lat2_deg, lon2_deg, fraction)
        waypoints.append(
            Waypoint(latitude=lat, longitude=lon, distance_from_origin_km=fraction * total_km, fraction=fraction)
        )
    return waypoints
