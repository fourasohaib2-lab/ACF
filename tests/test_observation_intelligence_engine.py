"""
REWRITTEN: every method used to ignore its own `state` argument and
return a fixed constant (33.5/9.5/19.5/66.5/20.83) regardless of the
real state passed in - same bug shape as the already-fixed
model4d.physics.numerical_forecast_integration.NumericalForecastIntegration.
A real observation-confidence/consistency/pattern/uncertainty score
needs a calibrated statistical/ML model, not just a single point state
- so each method now honestly raises NotImplementedError (or returns
None for intelligence_index()) instead of returning an invented
number. model4d_state_assimilation() used to aggregate the fake values
into one result; it now honestly reports that no real assimilation was
executed.
"""

import pytest

from acf.model4d.physics.observation_intelligence_engine import (
    ObservationIntelligenceEngine,
    ObservationIntelligenceState,
)


def create_state():

    return ObservationIntelligenceState(
        satellite_signal=80,
        radar_signal=75,
        assimilation_score=90,
        atmospheric_variability=20,
        cloud_confidence=30,
        temperature=290,
        humidity=15,
        observation_quality=8,
    )


def test_observation_confidence_score_not_implemented():

    model = ObservationIntelligenceEngine()

    with pytest.raises(NotImplementedError):
        model.observation_confidence_score(create_state())


def test_multi_sensor_consistency_not_implemented():

    model = ObservationIntelligenceEngine()

    with pytest.raises(NotImplementedError):
        model.multi_sensor_consistency(create_state())


def test_atmospheric_pattern_detection_not_implemented():

    model = ObservationIntelligenceEngine()

    with pytest.raises(NotImplementedError):
        model.atmospheric_pattern_detection(create_state())


def test_observation_uncertainty_not_implemented():

    model = ObservationIntelligenceEngine()

    with pytest.raises(NotImplementedError):
        model.observation_uncertainty(create_state())


def test_model4d_state_assimilation_no_longer_fabricates():

    model = ObservationIntelligenceEngine()

    result = model.model4d_state_assimilation(create_state())

    assert result["status"] == "NOT_EXECUTED_NO_ASSIMILATION_MODEL_CONNECTED"
    assert result["is_real_data"] is False


def test_intelligence_index_no_longer_fabricates():

    model = ObservationIntelligenceEngine()

    assert model.intelligence_index(create_state()) is None
