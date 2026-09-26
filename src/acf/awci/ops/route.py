"""
Route geometry for AWCI Web (spec SP4 §2): great-circle legs sampled at a fixed spacing.

Each leg follows the great circle between its end points, interpolated by spherical linear interpolation
(slerp) of unit vectors: for end points a, b with central angle omega = arccos(a . b),
    p(f) = [sin((1 - f) omega) a + sin(f omega) b] / sin(omega),   0 <= f <= 1.
Distance along the leg = omega * R, R = 6 371.0088 km, the IUGG mean Earth radius (Moritz 2000, Geodetic
Reference System 1980). The sphere departs from the WGS84 ellipsoid by at most about 0.5 % in distance.

Samples are spaced by at most `spacing_km` (default 10 km, under half a 0.25° cell): no grid cell crossed by the
route is skipped. Waypoints are always samples.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

EARTH_RADIUS_KM = 6371.0088  # IUGG mean radius R1 = (2a + b) / 3 of GRS80 (Moritz 2000)
MAX_WAYPOINTS = 20
MAX_ROUTE_KM = 10_000.0


class RouteError(ValueError):
    """Invalid route (points, length)."""


def _unit(lat: np.ndarray, lon: np.ndarray) -> np.ndarray:
    la, lo = np.radians(lat), np.radians(lon)
    return np.stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)], axis=-1)


def _latlon(v: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    lat = np.degrees(np.arctan2(v[..., 2], np.hypot(v[..., 0], v[..., 1])))
    lon = np.degrees(np.arctan2(v[..., 1], v[..., 0]))
    return lat, lon


def central_angle(a: tuple[float, float], b: tuple[float, float]) -> float:
    """Central angle (rad) between two (lat, lon) points; atan2 form, accurate for small and large angles."""
    ua, ub = _unit(np.array(a[0]), np.array(a[1])), _unit(np.array(b[0]), np.array(b[1]))
    return float(np.arctan2(np.linalg.norm(np.cross(ua, ub)), np.dot(ua, ub)))


def distance_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    return central_angle(a, b) * EARTH_RADIUS_KM


@dataclass(frozen=True)
class RouteSamples:
    lat: np.ndarray  # (n,)
    lon: np.ndarray  # (n,)
    distance_km: np.ndarray  # (n,) cumulative from the first waypoint
    waypoint_index: list[int]  # sample index of each waypoint
    length_km: float


def parse_points(spec: str) -> list[tuple[float, float]]:
    """'lat,lon;lat,lon;…' -> [(lat, lon), …], validated (2..20 points, finite, in range)."""
    points = []
    for part in spec.split(";"):
        fields = part.split(",")
        if len(fields) != 2:
            raise RouteError(f"point {part!r} is not 'lat,lon'")
        try:
            lat, lon = float(fields[0]), float(fields[1])
        except ValueError as exc:
            raise RouteError(f"point {part!r} is not numeric") from exc
        if not (np.isfinite(lat) and np.isfinite(lon) and -90 <= lat <= 90 and -180 <= lon <= 180):
            raise RouteError(f"point {part!r} is out of range")
        points.append((lat, lon))
    if not 2 <= len(points) <= MAX_WAYPOINTS:
        raise RouteError(f"a route has 2 to {MAX_WAYPOINTS} points, got {len(points)}")
    return points


def sample_route(points: Sequence[tuple[float, float]], spacing_km: float = 10.0) -> RouteSamples:
    if spacing_km <= 0:
        raise RouteError("spacing must be positive")
    lats: list[np.ndarray] = []
    lons: list[np.ndarray] = []
    dist: list[np.ndarray] = []
    waypoint_index = [0]
    start_km, count = 0.0, 0
    for k, (a, b) in enumerate(zip(points[:-1], points[1:])):
        omega = central_angle(a, b)
        leg_km = omega * EARTH_RADIUS_KM
        n = max(1, int(np.ceil(leg_km / spacing_km)))
        f = np.linspace(0.0, 1.0, n + 1)
        if k > 0:
            f = f[1:]  # the shared waypoint is already the last sample of the previous leg
        ua, ub = _unit(np.array(a[0]), np.array(a[1])), _unit(np.array(b[0]), np.array(b[1]))
        if omega < 1e-12:  # coincident points
            v = np.repeat(ua[None, :], len(f), axis=0)
        else:
            v = (np.sin((1 - f) * omega)[:, None] * ua + np.sin(f * omega)[:, None] * ub) / np.sin(omega)
        la, lo = _latlon(v)
        lats.append(la)
        lons.append(lo)
        dist.append(start_km + f * leg_km)
        count += len(f)
        waypoint_index.append(count - 1)
        start_km += leg_km
    if start_km > MAX_ROUTE_KM:
        raise RouteError(f"route of {start_km:.0f} km exceeds {MAX_ROUTE_KM:.0f} km")
    return RouteSamples(np.concatenate(lats), np.concatenate(lons), np.concatenate(dist), waypoint_index, start_km)
