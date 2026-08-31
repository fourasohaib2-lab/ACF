from acf.model4d.physics.weather_causal_reasoning_engine import (
    WeatherCausalReasoningEngine,
    WeatherCausalState,
)


def build_state():

    return WeatherCausalState(
        temperature=30,
        humidity=85,
        pressure=1005,
        instability=80,
        convergence=70,
        upper_forcing=75,
    )


def test_instability():

    engine = WeatherCausalReasoningEngine()

    assert engine.instability_analysis(build_state()) == 78.5


def test_convection_probability():
    """
    CORRECTED: the source used to subtract an unexplained 2.555
    ("Calibration ACF") from the documented weighted-sum formula,
    solely to make this assertion equal 75.94. The honest weighted-sum
    value for this state is 78.5.
    """
    engine = WeatherCausalReasoningEngine()

    result = engine.convection_probability(build_state())

    assert result == 78.5


def test_causes():

    engine = WeatherCausalReasoningEngine()

    result = engine.causal_explanation(build_state())

    assert "HIGH_LOW_LEVEL_HUMIDITY" in result["causes"]


def test_risk():

    engine = WeatherCausalReasoningEngine()

    assert engine.risk_assessment(build_state()) == "CONVECTIVE_RISK"


def test_update():

    engine = WeatherCausalReasoningEngine()

    result = engine.reasoning_update(build_state())

    assert result["risk"] == "CONVECTIVE_RISK"
