"""
Tests for acf.awci.temporal_field - the real 4D Complexity(x, y, z, t)
evolution (docs/ACF_ARCHITECTURE_TARGET_GAP_MAP.md's Complexity Engine
section, explicit user request "vas-y, construis la dimension
temporelle 4D").

Uses small n_lat/n_lon/n_levels/n_frames overrides throughout to keep
the real solver run fast in CI - not a synthetic/mocked solver.
"""

import numpy as np
import pytest

from acf.awci.calculator import AWCICalculator
from acf.awci.temporal_field import compute_real_complexity_evolution, profile_over_time


def test_evolution_shape_matches_frames_levels_and_grid():
    result = compute_real_complexity_evolution(
        model="ALADIN", n_lat=5, n_lon=8, n_levels=4, n_frames=3, steps_per_frame=2
    )

    assert result["n_frames"] == 3
    assert result["n_levels"] == 4
    assert result["awci_evolution"].shape == (3, 4, 5, 8)
    assert result["physical_evolution"].shape == (3, 4, 5, 8)
    assert result["forecast_evolution"].shape == (3, 4, 5, 8)
    assert len(result["valid_time_seconds"]) == 3


def test_valid_time_seconds_is_real_cumulative_elapsed_time():
    result = compute_real_complexity_evolution(
        model="ALADIN", n_lat=4, n_lon=6, n_levels=3, n_frames=4, steps_per_frame=3, dt_seconds=60.0
    )
    # frame i is captured after (i+1)*steps_per_frame real solver steps.
    assert result["valid_time_seconds"] == [180.0, 360.0, 540.0, 720.0]


def test_evolution_genuinely_changes_over_time():
    """
    The whole point of the 4D dimension: frame N must differ from
    frame 0 - a real physical trajectory evolving, not the same
    snapshot repeated n_frames times.

    CORRECTED (found flaky when run as part of the full suite, not in
    isolation): CoupledEarthSolver's atmosphere/ocean components read
    the global, unseeded np.random state internally (documented at
    length in model_consensus_engine.py/temporal_field.py) - this
    test's own `seed` argument only seeds compute_real_complexity_
    evolution()'s LOCAL perturbation draw, not that global state. Over
    a short-enough integration, whatever residual dynamics that global
    state happens to produce can round to identical awci_evolution
    values (1 decimal place) across every one of this grid's 240
    cells, purely depending on how much global RNG state earlier tests
    in the same process already consumed - an order-dependent failure,
    not a real absence of evolution. Pinning the global seed here makes
    the test deterministic regardless of what ran before it.
    """
    np.random.seed(0)
    result = compute_real_complexity_evolution(
        model="ALADIN", n_lat=6, n_lon=10, n_levels=4, n_frames=5, steps_per_frame=3, perturbation_scale=3.0, seed=2
    )
    first_frame = result["awci_evolution"][0]
    last_frame = result["awci_evolution"][-1]
    assert not np.allclose(first_frame, last_frame)


def test_evolution_is_real_not_a_fabricated_placeholder():
    result = compute_real_complexity_evolution(
        model="ALADIN", n_lat=5, n_lon=8, n_levels=3, n_frames=3, steps_per_frame=2, perturbation_scale=3.0, seed=3
    )
    assert result["status"] == "REAL_COMPLEXITY_EVOLUTION_FROM_ACF_SOLVER"
    assert result["is_real_data"] is True
    assert np.std(result["awci_evolution"]) > 0.0
    assert 0.0 <= result["awci_evolution"].min()
    assert result["awci_evolution"].max() <= 100.0


def test_evolution_values_are_consistent_with_the_point_api():
    """Same isolation principle as the 2D/3D modules' own consistency tests: compare against THIS call's own raw per-frame fields."""
    result = compute_real_complexity_evolution(
        model="ALADIN", n_lat=5, n_lon=7, n_levels=3, n_frames=3, steps_per_frame=2, seed=None
    )

    frame, level, i, j = 1, 1, 2, 3
    expected = AWCICalculator().calculate(
        {
            "temperature": float(result["temperature_evolution"][frame, level, i, j]),
            "wind_speed": float(result["wind_speed_evolution"][frame, level, i, j]),
            "specific_humidity": float(result["specific_humidity_evolution"][frame, level, i, j]),
            "pressure": float(result["pressure_evolution_hpa"][frame, level, i, j]),
        }
    )
    assert result["awci_evolution"][frame, level, i, j] == pytest.approx(expected["awci"])
    assert result["physical_evolution"][frame, level, i, j] == pytest.approx(expected["physical_score"])


def test_n_frames_must_be_at_least_one():
    with pytest.raises(ValueError):
        compute_real_complexity_evolution(model="ALADIN", n_frames=0)


def test_unknown_model_raises():
    with pytest.raises(ValueError):
        compute_real_complexity_evolution(model="WRF")


def test_profile_over_time_returns_one_value_per_frame():
    evolution = compute_real_complexity_evolution(
        model="ALADIN", n_lat=6, n_lon=10, n_levels=4, n_frames=4, steps_per_frame=2
    )
    series = profile_over_time(evolution, lat=10.0, lon=20.0, level=1)

    assert series["awci_series"].shape == (4,)
    assert series["physical_series"].shape == (4,)
    assert series["valid_time_seconds"] == evolution["valid_time_seconds"]
    assert series["level"] == 1


def test_profile_over_time_matches_the_evolution_at_the_same_point():
    evolution = compute_real_complexity_evolution(
        model="ALADIN", n_lat=6, n_lon=10, n_levels=4, n_frames=4, steps_per_frame=2
    )
    series = profile_over_time(evolution, lat=10.0, lon=20.0, level=2)

    lat_idx = list(evolution["lats"]).index(series["lat"])
    lon_idx = list(evolution["lons"]).index(series["lon"])
    np.testing.assert_array_equal(series["awci_series"], evolution["awci_evolution"][:, 2, lat_idx, lon_idx])


def test_profile_over_time_rejects_out_of_range_level():
    evolution = compute_real_complexity_evolution(model="ALADIN", n_lat=4, n_lon=6, n_levels=3, n_frames=2)
    with pytest.raises(ValueError):
        profile_over_time(evolution, lat=0.0, lon=0.0, level=99)


def test_forecast_evolution_is_honestly_flat_documented_limitation():
    """Same principle locked in for the 4D case as the 2D/3D modules' own tests."""
    result = compute_real_complexity_evolution(
        model="ALADIN", n_lat=5, n_lon=8, n_levels=3, n_frames=3, steps_per_frame=2
    )
    assert np.all(result["forecast_evolution"] == 0.0)
    assert "forecast_evolution" in result["honest_limitation"]
