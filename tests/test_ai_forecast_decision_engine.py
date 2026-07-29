from acf.model4d.physics.ai_forecast_decision_engine import (
    AIForecastDecisionEngine,
    AIForecastDecisionState,
)


def build_high_risk_state():
    return AIForecastDecisionState(
        hazard_index=85,
        confidence=90,
        forecast_quality=88,
        observation_quality=92,
        uncertainty=10,
    )


def test_decision_score():
    engine = AIForecastDecisionEngine()

    result = engine.decision_score(build_high_risk_state())

    assert result == 77.0


def test_confidence_level():
    engine = AIForecastDecisionEngine()

    result = engine.confidence_level(build_high_risk_state())

    assert result == "VERY_HIGH"


def test_recommended_action():
    engine = AIForecastDecisionEngine()

    result = engine.recommended_action(build_high_risk_state())

    assert result == "ISSUE_WEATHER_WARNING"


def test_priority_level():
    engine = AIForecastDecisionEngine()

    result = engine.priority_level(build_high_risk_state())

    assert result == 3


def test_automatic_response():
    engine = AIForecastDecisionEngine()

    result = engine.automatic_response(build_high_risk_state())

    assert result == "Issue official weather warning"


def test_model4d_ready():
    engine = AIForecastDecisionEngine()

    result = engine.model4d_ready(build_high_risk_state())

    assert result is True


def test_decision_update_keys():
    engine = AIForecastDecisionEngine()

    result = engine.decision_update(build_high_risk_state())

    assert "decision_score" in result
    assert "confidence_level" in result
    assert "recommended_action" in result
    assert "priority_level" in result
    assert "automatic_response" in result
    assert "model4d_ready" in result


def test_low_confidence_state():
    engine = AIForecastDecisionEngine()

    state = AIForecastDecisionState(
        hazard_index=30,
        confidence=40,
        forecast_quality=50,
        observation_quality=45,
        uncertainty=20,
    )

    assert engine.confidence_level(state) == "LOW"


def test_normal_operation():
    engine = AIForecastDecisionEngine()

    state = AIForecastDecisionState(
        hazard_index=10,
        confidence=90,
        forecast_quality=90,
        observation_quality=90,
        uncertainty=5,
    )

    assert engine.recommended_action(state) == "NORMAL_OPERATION"


def test_engine_creation():
    engine = AIForecastDecisionEngine()

    assert engine is not None
