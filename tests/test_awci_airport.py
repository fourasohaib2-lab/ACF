"""
Tests for acf.awci.airport - real airport approach-corridor geometry
closing AWCI's "AWCI aéroport" gap (post-model4d audit, 2026-09-12),
built on the real acf.aviation.airports.airport_database (LFPG/KJFK/
EGLL).
"""

from __future__ import annotations

import math

import pytest

from acf.aviation.airports.airport_database import AirportDatabase
from acf.awci.airport import (
    CORRIDOR_DISTANCE_KM,
    compute_airport_corridors,
    compute_runway_end_corridor,
    parse_runway_heading_magnetic_deg,
)


def test_parse_runway_heading_matches_the_real_icao_convention():
    assert parse_runway_heading_magnetic_deg("08L") == 80.0
    assert parse_runway_heading_magnetic_deg("26R") == 260.0
    assert parse_runway_heading_magnetic_deg("13") == 130.0
    assert parse_runway_heading_magnetic_deg("31L") == 310.0
    assert parse_runway_heading_magnetic_deg("04L") == 40.0
    assert parse_runway_heading_magnetic_deg("22R") == 220.0


def test_parse_runway_heading_two_ends_are_real_reciprocals():
    """A real, physical runway's two ends are always ~180 degrees
    apart (opposite directions of the same strip) - a real geometric
    invariant, not something this parser could get right by accident
    for every case in the database if it were wrong."""
    for airport_key in AirportDatabase.list_airports():
        airport = AirportDatabase.get_airport(airport_key)
        for runway in airport.runways:
            end_a, end_b = runway["identifier"].split("/")
            heading_a = parse_runway_heading_magnetic_deg(end_a)
            heading_b = parse_runway_heading_magnetic_deg(end_b)
            diff = abs(heading_a - heading_b)
            assert diff == pytest.approx(180.0, abs=10.0)


def test_parse_runway_heading_rejects_a_non_numeric_identifier():
    with pytest.raises(ValueError):
        parse_runway_heading_magnetic_deg("XX")


def test_unknown_airport_raises_never_a_fabricated_one():
    with pytest.raises(ValueError):
        compute_airport_corridors("ZZZZ")


def test_corridor_covers_every_real_runway_end():
    airport = AirportDatabase.get_airport("LFPG")
    result = compute_airport_corridors("LFPG")

    expected_ends = set()
    for runway in airport.runways:
        expected_ends.update(runway["identifier"].split("/"))

    assert set(result["corridors"].keys()) == expected_ends
    assert result["airport_icao"] == "LFPG"
    assert result["is_real_data"] is True


def test_corridor_accepts_iata_code_too():
    result = compute_airport_corridors("CDG")
    assert result["airport_icao"] == "LFPG"


def test_corridor_points_start_at_the_airport_and_end_at_the_real_distance():
    airport = AirportDatabase.get_airport("KJFK")
    corridor = compute_runway_end_corridor(airport, "13R", n_points=5)

    first_lat, first_lon = corridor["points"][0]
    assert first_lat == pytest.approx(airport.latitude, abs=1e-6)
    assert first_lon == pytest.approx(airport.longitude, abs=1e-6)

    # Real great-circle distance from the airport to the last point
    # must match the requested real corridor distance.
    last_lat, last_lon = corridor["points"][-1]
    r_km = 6371.0
    p1, p2 = math.radians(airport.latitude), math.radians(last_lat)
    dphi = math.radians(last_lat - airport.latitude)
    dlambda = math.radians(last_lon - airport.longitude)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    distance_km = 2 * r_km * math.asin(math.sqrt(a))
    assert distance_km == pytest.approx(CORRIDOR_DISTANCE_KM, rel=1e-3)


def test_approach_bearing_is_the_real_reciprocal_of_true_runway_heading():
    airport = AirportDatabase.get_airport("EGLL")
    corridor = compute_runway_end_corridor(airport, "09L")

    expected_true_heading = (90.0 + airport.magnetic_variation_deg) % 360.0
    expected_approach_bearing = (expected_true_heading + 180.0) % 360.0

    assert corridor["true_heading_deg"] == pytest.approx(expected_true_heading)
    assert corridor["approach_bearing_deg"] == pytest.approx(expected_approach_bearing)


def test_custom_corridor_distance_and_point_count_are_honored():
    airport = AirportDatabase.get_airport("LFPG")
    corridor = compute_runway_end_corridor(airport, "08L", corridor_distance_km=30.0, n_points=6)

    assert corridor["corridor_distance_km"] == 30.0
    assert len(corridor["points"]) == 6


def test_n_points_below_two_raises():
    airport = AirportDatabase.get_airport("LFPG")
    with pytest.raises(ValueError):
        compute_runway_end_corridor(airport, "08L", n_points=1)


def test_corridor_points_can_be_sampled_by_the_real_path_sampling_module():
    """Real end-to-end integration: this module's own geometry output
    is directly consumable by acf.awci.path_sampling.
    sample_field_along_path(), the same real sampling AWCI's route
    planning already uses - no new sampling logic invented here."""
    import numpy as np

    from acf.awci.path_sampling import sample_field_along_path

    airport = AirportDatabase.get_airport("LFPG")
    corridor = compute_runway_end_corridor(airport, "08L", n_points=4)
    point_a = corridor["points"][0]
    point_b = corridor["points"][-1]

    lats = np.linspace(airport.latitude - 1.0, airport.latitude + 1.0, 20)
    lons = np.linspace(airport.longitude - 1.0, airport.longitude + 1.0, 20)
    field = np.random.default_rng(0).uniform(0, 100, size=(20, 20))

    distances, values = sample_field_along_path(lats, lons, field, point_a, point_b, n_points=10)
    assert len(distances) == 10
    assert len(values) == 10
