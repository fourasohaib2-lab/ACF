"""
Tests for acf.gui.dashboard.awci_synthetic_field - previously untested.
Focus on awci_grid_full() (added 2026-09-02 for the Physical/Forecast
split), with light coverage of the pre-existing functions it builds on.
"""

import pytest

from acf.awci.hydrometeor_phase import compute_real_hydrometeor_phase_at_point
from acf.gui.dashboard.awci_synthetic_field import (
    _synthetic_inputs,
    awci_at,
    awci_grid,
    awci_grid_full,
    cross_section_field,
    cross_section_phase_severity_field,
)


def test_awci_at_returns_a_real_calculator_result():
    result = awci_at(36.7, 3.0, flight_level_hpa=300.0)
    assert 0.0 <= result["awci"] <= 100.0
    assert result["level"] in ["Very Low", "Low", "Moderate", "High", "Very High", "Extreme"]


def test_awci_grid_shape_matches_lat_lon_ranges():
    lons, lats, grid = awci_grid(lat_step=20.0, lon_step=40.0, lat_range=(-40.0, 40.0), lon_range=(-80.0, 80.0))
    assert len(grid) == len(lats)
    assert all(len(row) == len(lons) for row in grid)


def test_awci_grid_full_matches_awci_grid_composite_scores():
    """awci_grid_full()'s awci_field must be identical to awci_grid()'s own output - same underlying calc.calculate() calls."""
    kwargs = dict(lat_step=20.0, lon_step=40.0, lat_range=(-40.0, 40.0), lon_range=(-80.0, 80.0))
    lons, lats, awci_only = awci_grid(**kwargs)
    full = awci_grid_full(**kwargs)

    assert full["lons"] == lons
    assert full["lats"] == lats
    assert full["awci_field"] == awci_only


def test_awci_grid_full_physical_and_forecast_fields_are_populated():
    full = awci_grid_full(lat_step=20.0, lon_step=40.0, lat_range=(-40.0, 40.0), lon_range=(-80.0, 80.0))
    for row in full["physical_field"]:
        for value in row:
            assert value is not None
            assert 0.0 <= value <= 100.0
    for row in full["forecast_field"]:
        for value in row:
            assert value is not None
            assert 0.0 <= value <= 100.0


# ------------------------------- cross_section_phase_severity_field (dashboard parity)


def test_cross_section_phase_severity_field_shape_matches_cross_section_field():
    point_a, point_b = (36.75, 3.06), (32.90, 13.19)
    distances_awci, levels_awci, _ = cross_section_field(point_a, point_b, n_along=10, n_levels=5)
    distances, levels, grid = cross_section_phase_severity_field(point_a, point_b, n_along=10, n_levels=5)

    assert distances == distances_awci
    assert levels == levels_awci
    assert len(grid) == 5
    assert all(len(row) == 10 for row in grid)


def test_cross_section_phase_severity_field_matches_a_direct_formula_call():
    point_a, point_b = (36.75, 3.06), (32.90, 13.19)
    distances, levels, grid = cross_section_phase_severity_field(point_a, point_b, n_along=6, n_levels=4)

    level_i, dist_i = 2, 3
    hpa = levels[level_i]
    t = dist_i / 5
    lat = point_a[0] + t * (point_b[0] - point_a[0])
    lon = point_a[1] + t * (point_b[1] - point_a[1])
    inputs = _synthetic_inputs(lat, lon, hpa, 0.0)
    expected = compute_real_hydrometeor_phase_at_point(inputs["temperature"], inputs["specific_humidity"], hpa)

    assert grid[level_i][dist_i] == pytest.approx(expected["phase_severity"])


def test_cross_section_phase_severity_field_is_bounded_0_1():
    distances, levels, grid = cross_section_phase_severity_field((36.75, 3.06), (32.90, 13.19), n_along=10, n_levels=8)
    for row in grid:
        for value in row:
            assert 0.0 <= value <= 1.0
