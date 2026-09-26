"""Route geometry: great-circle distances, sampling, waypoints, antimeridian, input validation."""

import math

import numpy as np
import pytest

from acf.awci.ops.route import EARTH_RADIUS_KM, RouteError, distance_km, parse_points, sample_route


def _haversine(a: tuple[float, float], b: tuple[float, float]) -> float:
    """Independent formula (haversine) for the same spherical distance."""
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    dp, dl = p2 - p1, math.radians(b[1] - a[1])
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(h))


def test_known_distances() -> None:
    assert distance_km((0, 0), (90, 0)) == pytest.approx(math.pi / 2 * 6371.0088)  # quarter meridian
    daag, dtta = (36.691, 3.215), (36.851, 10.227)  # Algiers, Tunis-Carthage
    assert distance_km(daag, dtta) == pytest.approx(_haversine(daag, dtta), rel=1e-12)
    assert 620 < distance_km(daag, dtta) < 630
    assert distance_km(daag, daag) == 0.0


def test_samples_are_regular_on_the_great_circle_and_keep_the_waypoints() -> None:
    pts = [(36.691, 3.215), (36.851, 10.227), (33.875, 10.775)]  # DAAG, DTTA, DTTJ (Djerba)
    r = sample_route(pts, spacing_km=10)
    assert r.waypoint_index[0] == 0 and r.waypoint_index[-1] == len(r.lat) - 1
    for k, (lat, lon) in zip(r.waypoint_index, pts):
        assert r.lat[k] == pytest.approx(lat, abs=1e-9) and r.lon[k] == pytest.approx(lon, abs=1e-9)
    steps = np.diff(r.distance_km)
    assert steps.max() <= 10 + 1e-9 and steps.min() > 0
    chords = [distance_km((r.lat[i], r.lon[i]), (r.lat[i + 1], r.lon[i + 1])) for i in range(len(r.lat) - 1)]
    np.testing.assert_allclose(chords, steps, rtol=1e-9)  # samples lie on the great circle, distances consistent
    assert r.length_km == pytest.approx(distance_km(pts[0], pts[1]) + distance_km(pts[1], pts[2]))


def test_antimeridian_takes_the_short_way() -> None:
    r = sample_route([(0.0, 179.0), (0.0, -179.0)], spacing_km=20)
    assert r.length_km == pytest.approx(2 * math.pi / 180 * EARTH_RADIUS_KM)
    assert np.all(np.abs(r.lon) >= 179 - 1e-9)


@pytest.mark.parametrize("spec", ["36,3", "36,3;x,4", "36,3;95,4", "36,3;36", "36,3;nan,4",
                                  ";".join(["36,3"] * 21)])
def test_invalid_points(spec: str) -> None:
    with pytest.raises(RouteError):
        parse_points(spec)


def test_too_long_route() -> None:
    with pytest.raises(RouteError, match="exceeds"):
        sample_route([(0, 0), (0, 120)])  # 13 343 km
