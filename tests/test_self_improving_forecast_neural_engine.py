from acf.model4d.physics.self_improving_forecast_neural_engine import (
    SelfImprovingForecastNeuralEngine,
    SelfImprovingForecastState,
)


def build_state():

    return SelfImprovingForecastState(
        model_name="AROME",
        initial_accuracy=80,
        forecast_error=5,
        learning_rate=0.5,
        training_cycles=10,
        neural_confidence=90,
    )


def test_improvement_gain():

    engine = SelfImprovingForecastNeuralEngine()

    assert engine.improvement_gain(build_state()) == 5


def test_corrected_accuracy():

    engine = SelfImprovingForecastNeuralEngine()

    assert engine.corrected_accuracy(build_state()) == 84


def test_learning_score():

    engine = SelfImprovingForecastNeuralEngine()

    assert engine.neural_learning_score(build_state()) == 87


def test_status():

    engine = SelfImprovingForecastNeuralEngine()

    assert engine.optimization_status(build_state()) == "ACTIVE_LEARNING"


def test_learning_update():

    engine = SelfImprovingForecastNeuralEngine()

    result = engine.learning_update(build_state())

    assert result["model"] == "AROME"
    assert result["status"] == "ACTIVE_LEARNING"
