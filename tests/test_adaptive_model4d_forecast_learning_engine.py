from acf.model4d.physics.adaptive_model4d_forecast_learning_engine import (
    AdaptiveModel4DForecastLearningEngine,
    AdaptiveModel4DForecastState,
)


def build_state():

    return AdaptiveModel4DForecastState(
        model_name="ARPEGE",
        forecast_value=25,
        observed_value=30,
        previous_bias=2,
        model_weight=90,
        confidence=85,
    )


def test_forecast_error():

    engine = AdaptiveModel4DForecastLearningEngine()

    assert engine.forecast_error(build_state()) == 5


def test_bias_correction():

    engine = AdaptiveModel4DForecastLearningEngine()

    assert engine.bias_correction(build_state()) == 3.25


def test_adaptive_weight():

    engine = AdaptiveModel4DForecastLearningEngine()

    assert engine.adaptive_model_weight(build_state()) == 89.5


def test_learning_score():

    engine = AdaptiveModel4DForecastLearningEngine()

    assert engine.learning_score(build_state()) == 84.75


def test_model_update():

    engine = AdaptiveModel4DForecastLearningEngine()

    result = engine.model_update(build_state())

    assert result["model"] == "ARPEGE"
    assert result["forecast_error"] == 5
