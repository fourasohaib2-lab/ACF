"""
Tests for acf.model4d.physics.data_assimilation_engine.DataAssimilationEngine.

Rewritten: the previous version asserted hard-coded fake values
(299.5, 11.8, 1008.0, ...) that the old implementation always returned
regardless of input — the same class of bug as the fake METAR decoder
found earlier this session. These tests check real, verifiable OI/BLUE
behavior instead: known-gain edge cases and the exact formula.
"""

import pytest

from acf.model4d.physics.data_assimilation_engine import (
    DataAssimilationEngine,
    ModelState,
    ObservationState,
)


def create_model():
    return ModelState(temperature=300, humidity=10, pressure=100000, wind_speed=10, precipitation=3)


def create_observation():
    return ObservationState(temperature=299, humidity=12, pressure=100800, wind_speed=14, precipitation=5)


def test_oi_update_equal_errors_gives_midpoint():
    result = DataAssimilationEngine.optimal_interpolation_update(
        background=10.0, observation=20.0, background_error_std=1.0, observation_error_std=1.0
    )
    assert result == pytest.approx(15.0)


def test_oi_update_trusts_observation_when_background_error_dominates():
    result = DataAssimilationEngine.optimal_interpolation_update(
        background=10.0, observation=20.0, background_error_std=100.0, observation_error_std=0.001
    )
    assert result == pytest.approx(20.0, abs=0.1)


def test_oi_update_trusts_background_when_observation_error_dominates():
    result = DataAssimilationEngine.optimal_interpolation_update(
        background=10.0, observation=20.0, background_error_std=0.001, observation_error_std=100.0
    )
    assert result == pytest.approx(10.0, abs=0.1)


def test_oi_update_exact_formula():
    # sigma_b=2, sigma_o=1 -> K = 4/(4+1) = 0.8
    result = DataAssimilationEngine.optimal_interpolation_update(
        background=10.0, observation=20.0, background_error_std=2.0, observation_error_std=1.0
    )
    expected = 10.0 + 0.8 * (20.0 - 10.0)
    assert result == pytest.approx(expected)


def test_oi_update_invalid_negative_error():
    with pytest.raises(ValueError):
        DataAssimilationEngine.optimal_interpolation_update(10.0, 20.0, -1.0, 1.0)


def test_oi_update_invalid_both_zero_error():
    with pytest.raises(ValueError):
        DataAssimilationEngine.optimal_interpolation_update(10.0, 20.0, 0.0, 0.0)


def test_temperature_analysis_between_model_and_obs():
    engine = DataAssimilationEngine()
    result = engine.temperature_analysis(create_model(), create_observation(), 1.0, 1.0)
    # model.temperature=300, obs.temperature=299, equal errors -> midpoint 299.5
    assert result == pytest.approx(299.5)


def test_humidity_analysis_between_model_and_obs():
    engine = DataAssimilationEngine()
    result = engine.humidity_analysis(create_model(), create_observation(), 1.0, 1.0)
    assert result == pytest.approx(11.0)  # midpoint of 10 and 12


def test_pressure_analysis_weighted_toward_trusted_source():
    engine = DataAssimilationEngine()
    # Trust the observation much more (small obs error) -> analysis close to obs.pressure.
    result = engine.pressure_analysis(create_model(), create_observation(), 50.0, 1.0)
    assert result == pytest.approx(100800.0, abs=50.0)


def test_innovation_is_real_difference_not_hardcoded():
    engine = DataAssimilationEngine()
    innov = engine.innovation(create_model(), create_observation())
    assert innov["temperature"] == pytest.approx(299 - 300)
    assert innov["humidity"] == pytest.approx(12 - 10)
    assert innov["pressure"] == pytest.approx(100800 - 100000)
    assert innov["wind"] == pytest.approx(14 - 10)
    assert innov["precipitation"] == pytest.approx(5 - 3)


def test_assimilation_cycle_all_variables_present_and_consistent():
    engine = DataAssimilationEngine()
    result = engine.assimilation_cycle(create_model(), create_observation(), 1.0, 1.0)
    assert result["temperature"] == pytest.approx(299.5)
    assert result["humidity"] == pytest.approx(11.0)
    assert set(result.keys()) == {"temperature", "humidity", "pressure", "wind", "precipitation"}


def test_analysis_quality_index_perfect_match_is_100():
    engine = DataAssimilationEngine()
    perfect_obs = ObservationState(temperature=300, humidity=10, pressure=100000, wind_speed=10, precipitation=3)
    assert engine.analysis_quality_index(create_model(), perfect_obs) == pytest.approx(100.0)


def test_analysis_quality_index_lower_for_larger_discrepancy():
    engine = DataAssimilationEngine()
    close_obs = ObservationState(temperature=300, humidity=10, pressure=100000, wind_speed=10, precipitation=3.1)
    far_obs = ObservationState(temperature=350, humidity=10, pressure=100000, wind_speed=10, precipitation=3)
    q_close = engine.analysis_quality_index(create_model(), close_obs)
    q_far = engine.analysis_quality_index(create_model(), far_obs)
    assert q_close > q_far


def test_engine_no_longer_returns_old_hardcoded_stub_values():
    """
    Regression guard: with different error-std weightings, results
    must NOT collapse to the old hard-coded constants
    (299.5/11.8/1008.0/13.5/4.2/96.5) except where they coincidentally
    match a real midpoint (temperature, checked above).
    """
    engine = DataAssimilationEngine()
    # Heavily trust the model (small background error) -> analysis
    # should land near the model's own values, NOT the old fake ones.
    result = engine.assimilation_cycle(create_model(), create_observation(), 0.001, 100.0)
    assert result["humidity"] == pytest.approx(10.0, abs=0.5)  # near model, not the old fake 11.8
    assert result["pressure"] == pytest.approx(100000.0, abs=50.0)  # near model, not the old fake 1008.0 (wrong unit too)
    assert result["wind"] == pytest.approx(10.0, abs=0.5)  # near model, not the old fake 13.5
