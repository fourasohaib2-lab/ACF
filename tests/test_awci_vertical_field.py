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

from acf.awci.calculator import AWCICalculator
from acf.awci.vertical_field import (
    compute_real_complexity_volume,
    interpolated_state_at_pressure,
    vertical_profile_at_point,
    vertical_profile_at_standard_levels,
)


def test_volume_shape_matches_the_real_grid():
    result = compute_real_complexity_volume(model="ALADIN", n_lat=6, n_lon=10, n_levels=5, steps=2)

    assert result["n_levels"] == 5
    assert result["awci_volume"].shape == (5, 6, 10)
    assert result["physical_volume"].shape == (5, 6, 10)
    assert result["forecast_volume"].shape == (5, 6, 10)
    assert result["pressure_volume_hpa"].shape == (5, 6, 10)


def test_u_v_volumes_match_wind_speed_volume():
    """Real proof u_volume/v_volume (added 2026-09-03) are the SAME
    real components wind_speed_volume was already derived from, not a
    second/independent computation."""
    result = compute_real_complexity_volume(model="ALADIN", n_lat=4, n_lon=6, n_levels=5, steps=2)

    assert result["u_volume"].shape == result["wind_speed_volume"].shape
    assert result["v_volume"].shape == result["wind_speed_volume"].shape
    expected_speed = np.sqrt(result["u_volume"] ** 2 + result["v_volume"] ** 2)
    assert np.allclose(result["wind_speed_volume"], expected_speed)


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


# --------------------------------------- real vertical interpolation (2026-09-04, future-improvements.md #9)


def test_interpolated_state_matches_the_native_level_exactly_at_its_own_pressure():
    """A target pressure equal to one real native level's own pressure
    must interpolate to that exact real value (interpolation_fraction
    0.0) - not a value nudged toward its neighbour."""
    volume = compute_real_complexity_volume(model="ALADIN", n_lat=4, n_lon=6, n_levels=6, steps=2, seed=1)
    lats, lons = list(volume["lats"]), list(volume["lons"])
    lat_idx, lon_idx = 1, 2

    native_pressure = float(volume["pressure_volume_hpa"][0, lat_idx, lon_idx])
    state = interpolated_state_at_pressure(volume, lats[lat_idx], lons[lon_idx], native_pressure)

    assert state is not None
    assert state["interpolation_fraction"] == pytest.approx(0.0, abs=1e-9)
    assert state["temperature"] == pytest.approx(float(volume["temperature_volume"][0, lat_idx, lon_idx]))
    assert state["wind_speed"] == pytest.approx(float(volume["wind_speed_volume"][0, lat_idx, lon_idx]))


def test_interpolated_state_lies_between_its_two_real_bracketing_levels():
    volume = compute_real_complexity_volume(model="ALADIN", n_lat=4, n_lon=6, n_levels=6, steps=2, seed=1)
    lat, lon = float(volume["lats"][1]), float(volume["lons"][2])

    profile = vertical_profile_at_point(volume, lat, lon)
    p0, p1 = float(profile["pressure_profile_hpa"][0]), float(profile["pressure_profile_hpa"][1])
    target = (p0 + p1) / 2.0  # real midpoint between 2 real consecutive native levels

    state = interpolated_state_at_pressure(volume, lat, lon, target)

    assert state is not None
    assert state["native_bracket_levels"] == (0, 1)
    t0, t1 = float(profile["temperature_profile"][0]), float(profile["temperature_profile"][1])
    assert min(t0, t1) - 1e-6 <= state["temperature"] <= max(t0, t1) + 1e-6


def test_interpolated_state_is_none_outside_the_real_column_range():
    """Real, deliberate refusal to extrapolate (see module docstring) - a
    pressure far outside this column's real native range must not
    return a guessed value."""
    volume = compute_real_complexity_volume(model="ALADIN", n_lat=4, n_lon=6, n_levels=6, steps=2, seed=1)
    lat, lon = float(volume["lats"][0]), float(volume["lons"][0])

    assert interpolated_state_at_pressure(volume, lat, lon, 0.0001) is None  # far above the real column's top
    assert interpolated_state_at_pressure(volume, lat, lon, 1_000_000.0) is None  # far below its real surface


def test_vertical_profile_at_standard_levels_uses_a_real_calculator_on_real_interpolated_inputs():
    """Cross-check discipline: recompute AWCICalculator.calculate() on
    the SAME interpolation dict returned alongside each result and
    confirm they match byte-for-byte - the result is a real function of
    the real (interpolated) inputs, not a separately-fabricated
    number."""
    volume = compute_real_complexity_volume(model="ALADIN", n_lat=4, n_lon=6, n_levels=6, steps=2, seed=1)
    lat, lon = float(volume["lats"][1]), float(volume["lons"][2])
    profile = vertical_profile_at_point(volume, lat, lon)
    p0 = float(profile["pressure_profile_hpa"][0])

    result_map = vertical_profile_at_standard_levels(volume, lat, lon, {"native-0": p0})

    assert "native-0" in result_map
    entry = result_map["native-0"]
    expected = AWCICalculator().calculate(
        {
            "temperature": entry["interpolation"]["temperature"],
            "wind_speed": entry["interpolation"]["wind_speed"],
            "specific_humidity": entry["interpolation"]["specific_humidity"],
            "pressure": entry["interpolation"]["pressure"],
        }
    )
    assert entry["result"]["awci"] == pytest.approx(expected["awci"])
    assert set(entry["result"]["module_scores"].keys()) == {
        "dynamic", "thermodynamic", "convective", "microphysical", "topographic", "temporal", "confidence",
        "ensemble_spread", "model_disagreement",
    }


def test_vertical_profile_at_standard_levels_omits_out_of_range_labels_honestly():
    volume = compute_real_complexity_volume(model="ALADIN", n_lat=4, n_lon=6, n_levels=6, steps=2, seed=1)
    lat, lon = float(volume["lats"][0]), float(volume["lons"][0])
    profile = vertical_profile_at_point(volume, lat, lon)
    real_hpa = float(profile["pressure_profile_hpa"][0])

    result_map = vertical_profile_at_standard_levels(
        volume, lat, lon, {"real": real_hpa, "impossible": 1_000_000.0}
    )

    assert "real" in result_map
    assert "impossible" not in result_map  # honestly omitted, never a fabricated/extrapolated entry
