"""
Tests for acf.awci.spatial_field - the real 2D Complexity(x, y) field
(docs/ACF_ARCHITECTURE_TARGET_GAP_MAP.md's Complexity Engine section,
explicit user request "vas-y, construis la dimension spatiale 2D").

Uses small n_lat/n_lon overrides throughout to keep the real solver run
fast in CI, per compute_real_complexity_field()'s own override params -
not a synthetic/mocked solver.
"""

import numpy as np
import pytest

from acf.awci.spatial_field import compute_real_complexity_field


def test_field_shape_matches_the_real_grid():
    result = compute_real_complexity_field(model="ALADIN", n_lat=6, n_lon=10, n_levels=4, steps=2)

    assert len(result["lats"]) == 6
    assert len(result["lons"]) == 10
    assert result["awci_field"].shape == (6, 10)
    assert result["physical_field"].shape == (6, 10)
    assert result["forecast_field"].shape == (6, 10)


def test_field_is_real_not_a_fabricated_placeholder():
    result = compute_real_complexity_field(
        model="ALADIN", n_lat=8, n_lon=14, n_levels=4, steps=6, perturbation_scale=3.0, seed=1
    )

    assert result["status"] == "REAL_COMPLEXITY_FIELD_FROM_ACF_SOLVER"
    assert result["is_real_data"] is True
    # A real physics field with a genuine spatial perturbation must not
    # be perfectly uniform - that would mean the "field" is secretly a
    # single scalar broadcast, not real per-point solver output.
    assert np.std(result["awci_field"]) > 0.0
    assert 0.0 <= result["awci_field"].min()
    assert result["awci_field"].max() <= 100.0


def test_field_values_are_consistent_with_the_point_api():
    """
    Spot-check one grid cell against the well-tested point-level
    AWCICalculator.calculate() path directly, fed with THIS call's own
    returned raw field values (temperature_field/wind_speed_field/...)
    - not a second, independent solver run. CoupledEarthSolver's
    atmosphere/ocean components are not bit-reproducible across
    separate runs (see ModelConsensusEngine.
    compute_real_multi_model_disagreement()'s own note), so comparing
    against a fresh run would spuriously fail; comparing against the
    exact values this call already used correctly isolates "does
    spatial_field.py compute the same thing AWCICalculator would" from
    "is the solver deterministic" (a separate, pre-existing question).
    """
    from acf.awci.calculator import AWCICalculator

    result = compute_real_complexity_field(model="ALADIN", n_lat=6, n_lon=10, n_levels=4, steps=2, seed=None)

    i, j = 2, 3
    expected = AWCICalculator().calculate(
        {
            "temperature": float(result["temperature_field"][i, j]),
            "wind_speed": float(result["wind_speed_field"][i, j]),
            "specific_humidity": float(result["specific_humidity_field"][i, j]),
            "pressure": float(result["pressure_field_hpa"][i, j]),
        }
    )
    assert result["awci_field"][i, j] == pytest.approx(expected["awci"])
    assert result["physical_field"][i, j] == pytest.approx(expected["physical_score"])
    assert result["forecast_field"][i, j] == pytest.approx(expected["forecast_score"])


def test_forecast_field_has_no_nan_with_default_weights():
    """
    With AWCICalculator's DEFAULT_WEIGHTS, the 'confidence' module alone
    has nonzero weight (0.05), so forecast_score is always defined -
    the forecast_field must not contain the "undefined" np.nan sentinel
    anywhere under default weights.
    """
    result = compute_real_complexity_field(model="ALADIN", n_lat=5, n_lon=8, n_levels=4, steps=2)
    assert not np.isnan(result["forecast_field"]).any()


def test_forecast_field_is_honestly_flat_documented_limitation():
    """
    Locks in the honest limitation documented in spatial_field.py's own
    docstring/honest_limitation string: no per-point ensemble/model
    data is computed per grid cell (too expensive - see module
    docstring), so forecast_field is exactly 0.0 everywhere under
    default weights - a real result (not fabricated), but not yet a
    real spatial forecast-uncertainty signal. If this ever legitimately
    changes (e.g. per-point forecast data gets wired in), this test
    should be updated deliberately, not silently left failing.
    """
    result = compute_real_complexity_field(model="ALADIN", n_lat=5, n_lon=8, n_levels=4, steps=2)
    assert np.all(result["forecast_field"] == 0.0)
    assert "forecast_field" in result["honest_limitation"]


def test_unknown_model_raises():
    with pytest.raises(ValueError):
        compute_real_complexity_field(model="WRF")


def test_disabling_perturbation_gives_a_flat_field_from_the_uniform_initial_state():
    """
    seed=None (no perturbation) with few steps from CoupledEarthSolver's
    uniform initial state should produce an almost-flat field - the
    opposite case of test_field_is_real_not_a_fabricated_placeholder(),
    confirming the variation seen there really comes from the
    perturbation/dynamics, not from some hidden per-cell randomness in
    this module itself.
    """
    result = compute_real_complexity_field(model="ALADIN", n_lat=6, n_lon=10, n_levels=4, steps=1, seed=None)
    assert np.std(result["awci_field"]) < 1.0


def test_raw_state_fields_are_returned_with_matching_shape():
    result = compute_real_complexity_field(model="ALADIN", n_lat=5, n_lon=9, n_levels=4, steps=1)
    for key in ("temperature_field", "wind_speed_field", "specific_humidity_field", "pressure_field_hpa"):
        assert result[key].shape == (5, 9)
    # Wind speed is a magnitude - never negative.
    assert (result["wind_speed_field"] >= 0.0).all()


def test_fields_used_documents_the_honest_scope():
    result = compute_real_complexity_field(model="ALADIN", n_lat=4, n_lon=6, n_levels=4, steps=1)
    assert set(result["fields_used"]) == {"temperature", "wind_speed", "specific_humidity", "pressure"}
    assert "cape" not in result["fields_used"]
    assert result["is_real_data"] is True
