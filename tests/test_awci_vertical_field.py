"""
Tests for acf.awci.vertical_field - the real 3D Complexity(x, y, z)
volume (docs/ACF_ARCHITECTURE_TARGET_GAP_MAP.md's Complexity Engine
section, explicit user request "vas-y, construis la dimension
verticale 3D").

Uses small n_lat/n_lon/n_levels overrides throughout to keep the real
solver run fast in CI - not a synthetic/mocked solver.
"""

import numpy as np
import pytest

from acf.awci.vertical_field import compute_real_complexity_volume, vertical_profile_at_point


def test_volume_shape_matches_the_real_grid():
    result = compute_real_complexity_volume(model="ALADIN", n_lat=6, n_lon=10, n_levels=5, steps=2)

    assert result["n_levels"] == 5
    assert result["awci_volume"].shape == (5, 6, 10)
    assert result["physical_volume"].shape == (5, 6, 10)
    assert result["forecast_volume"].shape == (5, 6, 10)
    assert result["pressure_volume_hpa"].shape == (5, 6, 10)


def test_pressure_decreases_with_altitude_real_physics():
    """
    Real physical invariant, verified against actual solver output (not
    assumed): level 0 is the surface (highest pressure), increasing
    level index means increasing altitude and DEcreasing pressure -
    the same convention confirmed earlier this session against
    CoupledEarthSolver.compute_interfacial_fluxes()'s own
    surface_temp = state["T"][0, :, :].
    """
    result = compute_real_complexity_volume(model="ALADIN", n_lat=4, n_lon=6, n_levels=6, steps=2)
    mean_pressure_by_level = result["pressure_volume_hpa"].mean(axis=(1, 2))

    assert all(
        mean_pressure_by_level[level] > mean_pressure_by_level[level + 1]
        for level in range(len(mean_pressure_by_level) - 1)
    )


def test_volume_is_real_not_a_fabricated_placeholder():
    result = compute_real_complexity_volume(
        model="ALADIN", n_lat=6, n_lon=10, n_levels=5, steps=6, perturbation_scale=3.0, seed=1
    )

    assert result["status"] == "REAL_COMPLEXITY_VOLUME_FROM_ACF_SOLVER"
    assert result["is_real_data"] is True
    # Genuine spatial AND vertical variation - not one score broadcast
    # across the whole volume.
    assert np.std(result["awci_volume"]) > 0.0
    # Different levels must not be identical copies of each other.
    assert not np.allclose(result["awci_volume"][0], result["awci_volume"][-1])
    assert 0.0 <= result["awci_volume"].min()
    assert result["awci_volume"].max() <= 100.0


def test_volume_values_are_consistent_with_the_point_api():
    """Same isolation principle as test_awci_spatial_field.py's own consistency test - compare against THIS call's own raw fields, not a second solver run."""
    from acf.awci.calculator import AWCICalculator

    result = compute_real_complexity_volume(model="ALADIN", n_lat=5, n_lon=7, n_levels=4, steps=2, seed=None)

    level, i, j = 2, 1, 4
    expected = AWCICalculator().calculate(
        {
            "temperature": float(result["temperature_volume"][level, i, j]),
            "wind_speed": float(result["wind_speed_volume"][level, i, j]),
            "specific_humidity": float(result["specific_humidity_volume"][level, i, j]),
            "pressure": float(result["pressure_volume_hpa"][level, i, j]),
        }
    )
    assert result["awci_volume"][level, i, j] == pytest.approx(expected["awci"])
    assert result["physical_volume"][level, i, j] == pytest.approx(expected["physical_score"])


def test_unknown_model_raises():
    with pytest.raises(ValueError):
        compute_real_complexity_volume(model="WRF")


def test_vertical_profile_at_point_returns_one_value_per_level():
    volume = compute_real_complexity_volume(model="ALADIN", n_lat=6, n_lon=10, n_levels=5, steps=2)
    profile = vertical_profile_at_point(volume, lat=10.0, lon=20.0)

    assert profile["awci_profile"].shape == (5,)
    assert profile["physical_profile"].shape == (5,)
    assert profile["pressure_profile_hpa"].shape == (5,)
    # Nearest-neighbour lookup must land on one of the volume's real coordinates.
    assert profile["lat"] in list(volume["lats"])
    assert profile["lon"] in list(volume["lons"])


def test_vertical_profile_matches_the_volume_at_the_same_point():
    volume = compute_real_complexity_volume(model="ALADIN", n_lat=6, n_lon=10, n_levels=5, steps=2)
    profile = vertical_profile_at_point(volume, lat=10.0, lon=20.0)

    lat_idx = list(volume["lats"]).index(profile["lat"])
    lon_idx = list(volume["lons"]).index(profile["lon"])
    np.testing.assert_array_equal(profile["awci_profile"], volume["awci_volume"][:, lat_idx, lon_idx])


def test_forecast_volume_is_honestly_flat_documented_limitation():
    """Same principle locked in for the 3D case as spatial_field.py's 2D test."""
    result = compute_real_complexity_volume(model="ALADIN", n_lat=5, n_lon=8, n_levels=4, steps=2)
    assert np.all(result["forecast_volume"] == 0.0)
    assert "forecast_volume" in result["honest_limitation"]
