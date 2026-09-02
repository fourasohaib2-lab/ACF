"""
Tests for acf.gui.dashboard.awci_synthetic_field - previously untested.
Focus on awci_grid_full() (added 2026-09-02 for the Physical/Forecast
split), with light coverage of the pre-existing functions it builds on.
"""

from acf.gui.dashboard.awci_synthetic_field import awci_at, awci_grid, awci_grid_full


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
