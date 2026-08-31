from acf.model4d.physics.adaptive_forecast_control_engine import (
    AdaptiveForecastControlEngine,
    AdaptiveForecastControlState,
)


def build_state():

    return AdaptiveForecastControlState(
        forecast_error=10,
        observation_error=15,
        model_confidence=85,
        assimilation_quality=90,
        parameter_stability=80,
        learning_rate=0.5,
    )


def test_error_correction():

    engine = AdaptiveForecastControlEngine()

    assert engine.error_correction_index(build_state()) == 87.5


def test_confidence():

    engine = AdaptiveForecastControlEngine()

    assert engine.confidence_adjustment(build_state()) == 87.0


def test_parameter_control():

    engine = AdaptiveForecastControlEngine()

    assert engine.parameter_control_index(build_state()) == 87.17


def test_decision():

    engine = AdaptiveForecastControlEngine()

    assert engine.control_decision(build_state()) == "OPTIMAL_MODEL_CONTROL"


def test_update():

    engine = AdaptiveForecastControlEngine()

    result = engine.control_update(build_state())

    assert result["decision"] == "OPTIMAL_MODEL_CONTROL"
