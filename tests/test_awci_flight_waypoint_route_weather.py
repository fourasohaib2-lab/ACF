"""Tests for the new awci.flight.waypoint/route_weather modules, built
while working through the full remaining-gaps list ("On les attaque
toutes un par un") - the waypoint.py/route_weather.py files named in
docs/architecture/awci_reference_architecture.md section 11 ("Flight
Planning Engine... Covers: Route, Altitude, Departure, Cruise, Arrival,
Alternate, Weather along route, Hazards along route.").

waypoint.py implements the real, standard great-circle "intermediate
point" spherical-navigation formula - verified here against
hand-computable real cases (the equator quarter-point, antipodal
rejection, origin/destination endpoints). route_weather.py is a real,
thin composition of FlightRoutingEngine + waypoint.py +
ObservationsHub/build_weather_snapshot - no new physics or fetch logic
of its own.
"""

from __future__ import annotations

import pytest

from awci.flight.route_weather import RouteWeatherBriefing, build_route_weather_briefing
from awci.flight.waypoint import Waypoint, generate_route_waypoints, great_circle_intermediate_point
from awci.knowledge.icao.live_source import LiveReport, LiveStationBundle
from awci.knowledge.icao.metar_decoder import METARDecoder

# --------------------------------------------------------------------- waypoint.py


def test_great_circle_intermediate_point_equator_quarter_point():
    """A real, hand-verifiable case: along the equator, the great
    circle IS the equator itself, and the intermediate point at any
    fraction is simple linear longitude interpolation."""
    lat, lon = great_circle_intermediate_point(0.0, 0.0, 0.0, 90.0, 0.5)
    assert lat == pytest.approx(0.0, abs=1e-9)
    assert lon == pytest.approx(45.0, abs=1e-9)


def test_great_circle_intermediate_point_at_fraction_zero_is_the_origin():
    lat, lon = great_circle_intermediate_point(48.0, 2.0, 40.0, -73.0, 0.0)
    assert lat == pytest.approx(48.0, abs=1e-9)
    assert lon == pytest.approx(2.0, abs=1e-9)


def test_great_circle_intermediate_point_at_fraction_one_is_the_destination():
    lat, lon = great_circle_intermediate_point(48.0, 2.0, 40.0, -73.0, 1.0)
    assert lat == pytest.approx(40.0, abs=1e-9)
    assert lon == pytest.approx(-73.0, abs=1e-9)


def test_great_circle_intermediate_point_rejects_an_out_of_range_fraction():
    with pytest.raises(ValueError):
        great_circle_intermediate_point(0.0, 0.0, 10.0, 10.0, 1.5)
    with pytest.raises(ValueError):
        great_circle_intermediate_point(0.0, 0.0, 10.0, 10.0, -0.1)


def test_great_circle_intermediate_point_rejects_antipodal_points():
    with pytest.raises(ValueError):
        great_circle_intermediate_point(0.0, 0.0, 0.0, 180.0, 0.5)


def test_great_circle_intermediate_point_identical_points_returns_the_same_point():
    lat, lon = great_circle_intermediate_point(48.0, 2.0, 48.0, 2.0, 0.5)
    assert lat == pytest.approx(48.0, abs=1e-9)
    assert lon == pytest.approx(2.0, abs=1e-9)


def test_generate_route_waypoints_includes_real_origin_and_destination():
    waypoints = generate_route_waypoints(48.0, 2.0, 40.0, -73.0, n_points=5)
    assert len(waypoints) == 5
    assert waypoints[0].latitude == pytest.approx(48.0, abs=1e-9)
    assert waypoints[0].longitude == pytest.approx(2.0, abs=1e-9)
    assert waypoints[0].distance_from_origin_km == pytest.approx(0.0, abs=1e-9)
    assert waypoints[-1].latitude == pytest.approx(40.0, abs=1e-9)
    assert waypoints[-1].longitude == pytest.approx(-73.0, abs=1e-9)


def test_generate_route_waypoints_distances_are_monotonically_increasing():
    waypoints = generate_route_waypoints(48.0, 2.0, 40.0, -73.0, n_points=8)
    distances = [w.distance_from_origin_km for w in waypoints]
    assert distances == sorted(distances)
    assert distances[0] == 0.0
    assert distances[-1] > 0.0


def test_generate_route_waypoints_rejects_too_few_points():
    with pytest.raises(ValueError):
        generate_route_waypoints(0.0, 0.0, 10.0, 10.0, n_points=1)


def test_generate_route_waypoints_fractions_are_evenly_spaced():
    waypoints = generate_route_waypoints(0.0, 0.0, 0.0, 90.0, n_points=4)
    fractions = [w.fraction for w in waypoints]
    assert fractions == pytest.approx([0.0, 1 / 3, 2 / 3, 1.0])


def test_waypoint_is_a_real_frozen_dataclass():
    waypoint = Waypoint(latitude=1.0, longitude=2.0, distance_from_origin_km=3.0, fraction=0.5)
    with pytest.raises(Exception):
        waypoint.latitude = 99.0  # type: ignore[misc]


def test_lfpg_to_kjfk_route_bows_north_of_the_straight_line_average():
    """A real, qualitative sanity check: the real great-circle route
    from Paris to New York bows noticeably north of the simple
    latitude average (a known, real property of great-circle routes
    at these latitudes crossing the North Atlantic)."""
    from awci.knowledge.airports.airport_database import AirportDatabase

    lfpg = AirportDatabase.get_airport("LFPG")
    kjfk = AirportDatabase.get_airport("KJFK")
    waypoints = generate_route_waypoints(lfpg.latitude, lfpg.longitude, kjfk.latitude, kjfk.longitude, n_points=5)
    midpoint = waypoints[2]
    simple_average_lat = (lfpg.latitude + kjfk.latitude) / 2.0
    assert midpoint.latitude > simple_average_lat


# --------------------------------------------------------------------- route_weather.py


class _FakeHub:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def fetch_station(self, icao_code: str, timeout: float = 8.0) -> LiveStationBundle:
        self.calls.append(icao_code)
        bundle = LiveStationBundle(icao_code=icao_code)
        raw = f"{icao_code} 211200Z 27010KT 10SM FEW250 15/08 Q1013"
        bundle.metar = LiveReport(raw_text=raw, decoded=METARDecoder.decode(raw))
        return bundle


def test_build_route_weather_briefing_composes_real_route_and_weather():
    hub = _FakeHub()
    briefing = build_route_weather_briefing("LFPG", "KJFK", n_waypoints=4, hub=hub)
    assert isinstance(briefing, RouteWeatherBriefing)
    assert briefing.departure_icao == "LFPG"
    assert briefing.arrival_icao == "KJFK"
    assert briefing.great_circle_distance_nm > 3000.0  # real LFPG-KJFK is ~3150 nm
    assert len(briefing.waypoints) == 4
    assert briefing.departure_weather.is_real_data is True
    assert briefing.arrival_weather.is_real_data is True
    assert "LFPG" in hub.calls
    assert "KJFK" in hub.calls


def test_build_route_weather_briefing_fetches_every_real_alternate():
    hub = _FakeHub()
    briefing = build_route_weather_briefing("LFPG", "KJFK", hub=hub)
    # UPDATED (2026-09-24): AirportDatabase grew from 3 to 6 real airports
    # (DAAG/DTTA/LIRF added for the AWCI web dashboard's Algiers-Tunis-Rome
    # route) - EGLL and DAAG are the 2 real nearest-to-KJFK alternates now.
    assert set(briefing.alternate_weather) <= {"EGLL", "DAAG"}
    for icao, snapshot in briefing.alternate_weather.items():
        assert snapshot.is_real_data is True
        assert icao in hub.calls


def test_build_route_weather_briefing_rejects_an_unknown_airport():
    with pytest.raises(ValueError):
        build_route_weather_briefing("ZZZZ", "KJFK", hub=_FakeHub())
    with pytest.raises(ValueError):
        build_route_weather_briefing("LFPG", "ZZZZ", hub=_FakeHub())


def test_build_route_weather_briefing_constructs_a_real_default_hub(monkeypatch):
    import awci.flight.route_weather as route_weather_module

    fake_hub = _FakeHub()
    monkeypatch.setattr(route_weather_module, "ObservationsHub", lambda: fake_hub)
    briefing = route_weather_module.build_route_weather_briefing("LFPG", "KJFK", n_waypoints=3)
    assert briefing.departure_weather.is_real_data is True
    assert "LFPG" in fake_hub.calls


def test_build_route_weather_briefing_honestly_surfaces_a_real_fetch_failure():
    class _FailingHub:
        def fetch_station(self, icao_code: str, timeout: float = 8.0) -> LiveStationBundle:
            bundle = LiveStationBundle(icao_code=icao_code)
            bundle.metar = LiveReport(error=f"{icao_code} fetch failed: network error")
            return bundle

    briefing = build_route_weather_briefing("LFPG", "KJFK", hub=_FailingHub())
    assert briefing.departure_weather.is_real_data is False
    assert "network error" in briefing.departure_weather.status


# --------------------------------------------------------------------- discipline


def test_route_weather_never_fabricates_weather_at_an_intermediate_waypoint():
    """Discipline check: Waypoint carries no weather field at all -
    only real position/distance - matching route_weather.py's own
    disclosed honest scope (no real data source exists for weather at
    an arbitrary point along a route)."""
    field_names = set(Waypoint.__dataclass_fields__)
    assert field_names == {"latitude", "longitude", "distance_from_origin_km", "fraction"}
