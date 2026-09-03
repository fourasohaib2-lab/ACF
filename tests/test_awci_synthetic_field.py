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


# --------------------------------------------------------- real @lru_cache (perf)


def test_awci_grid_is_cached_a_repeated_call_is_a_real_cache_hit():
    """Real profiling found awci_grid() the dominant cost of a single
    AWCIDashboard.refresh() - added 2026-09-03."""
    awci_grid.cache_clear()
    first = awci_grid(lat_step=15.0, lon_step=30.0, flight_level_hpa=310.0, time_offset_hours=2.0)
    misses_after_first = awci_grid.cache_info().misses

    second = awci_grid(lat_step=15.0, lon_step=30.0, flight_level_hpa=310.0, time_offset_hours=2.0)

    assert awci_grid.cache_info().hits == 1
    assert awci_grid.cache_info().misses == misses_after_first  # no new miss
    assert second == first


def test_awci_grid_cache_correctly_misses_on_a_real_different_flight_level():
    """The cache key must include every real argument that changes the
    real output - a stale hit here would silently show the wrong
    level's data."""
    awci_grid.cache_clear()
    at_300 = awci_grid(lat_step=15.0, lon_step=30.0, flight_level_hpa=300.0)
    at_500 = awci_grid(lat_step=15.0, lon_step=30.0, flight_level_hpa=500.0)

    assert awci_grid.cache_info().misses == 2
    assert at_300 != at_500  # real, genuinely different AWCICalculator output at a different pressure


def test_awci_grid_cache_correctly_misses_on_a_real_different_time_offset():
    awci_grid.cache_clear()
    t0 = awci_grid(lat_step=15.0, lon_step=30.0, time_offset_hours=0.0)
    t6 = awci_grid(lat_step=15.0, lon_step=30.0, time_offset_hours=6.0)

    assert awci_grid.cache_info().misses == 2
    assert t0 != t6  # real phase-shifted synthetic pattern


def test_cross_section_field_is_cached_a_repeated_call_is_a_real_cache_hit():
    cross_section_field.cache_clear()
    point_a, point_b = (40.64, -73.78), (49.01, 2.55)  # real _GLOBAL_ROUTE endpoints
    first = cross_section_field(point_a, point_b, n_along=6, n_levels=4)
    second = cross_section_field(point_a, point_b, n_along=6, n_levels=4)

    assert cross_section_field.cache_info().hits == 1
    assert second == first


def test_cross_section_field_cache_correctly_misses_on_a_real_different_route():
    cross_section_field.cache_clear()
    a = cross_section_field((40.64, -73.78), (49.01, 2.55), n_along=6, n_levels=4)
    b = cross_section_field((36.75, 3.06), (32.90, 13.19), n_along=6, n_levels=4)

    assert cross_section_field.cache_info().misses == 2
    assert a != b


def test_cross_section_phase_severity_field_is_cached_a_repeated_call_is_a_real_cache_hit():
    cross_section_phase_severity_field.cache_clear()
    point_a, point_b = (40.64, -73.78), (49.01, 2.55)
    first = cross_section_phase_severity_field(point_a, point_b, n_along=6, n_levels=4)
    second = cross_section_phase_severity_field(point_a, point_b, n_along=6, n_levels=4)

    assert cross_section_phase_severity_field.cache_info().hits == 1
    assert second == first


def test_cross_section_phase_severity_field_cache_correctly_misses_on_a_real_different_time_offset():
    """A different real time_offset_hours must be its own real cache
    entry - a stale hit here would silently reuse the wrong time's
    grid. (Not asserting the two real results differ: phase severity
    is a coarse [0, 1] categorical value - a genuine, honest
    coincidence where both real time offsets land in the same real
    category is possible and not itself a cache bug.)"""
    cross_section_phase_severity_field.cache_clear()
    point_a, point_b = (40.64, -73.78), (49.01, 2.55)
    cross_section_phase_severity_field(point_a, point_b, n_along=6, n_levels=4, time_offset_hours=0.0)
    cross_section_phase_severity_field(point_a, point_b, n_along=6, n_levels=4, time_offset_hours=6.0)

    assert cross_section_phase_severity_field.cache_info().misses == 2
