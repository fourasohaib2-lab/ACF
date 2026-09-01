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
    """
    CORRECTED: used to subtract an unexplained 0.5 with no comment or
    justification, present only to make this exact assertion (87.0)
    match. The honest plain average is 87.5.
    """

    engine = AdaptiveForecastControlEngine()

    assert engine.confidence_adjustment(build_state()) == 87.5


def test_parameter_control():
    """
    CORRECTED: used to add an unexplained 1.395 with no comment or
    justification, present only to make this exact assertion (87.17)
    match. The honest weighted sum (using the now-honest
    confidence_adjustment) is 86.0.
    """

    engine = AdaptiveForecastControlEngine()

    assert engine.parameter_control_index(build_state()) == 86.0


def test_decision():

    engine = AdaptiveForecastControlEngine()

    assert engine.control_decision(build_state()) == "OPTIMAL_MODEL_CONTROL"


def test_update():

    engine = AdaptiveForecastControlEngine()

    result = engine.control_update(build_state())

    assert result["decision"] == "OPTIMAL_MODEL_CONTROL"
