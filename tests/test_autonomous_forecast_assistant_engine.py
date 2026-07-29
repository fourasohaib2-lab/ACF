from acf.model4d.physics.autonomous_forecast_assistant_engine import (
    AutonomousForecastAssistantEngine,
    AutonomousForecastAssistantState,
)


def build_state():
    return AutonomousForecastAssistantState(
        model_sources=[
            "ARPEGE",
            "AROME",
            "WRF",
            "ICON",
        ],
        ensemble_score=80,
        confidence=85,
        hazard_level=75,
        observation_quality=90,
        uncertainty=10,
        region="Algeria",
    )


def test_available_models():
    engine = AutonomousForecastAssistantEngine()

    assert engine.available_models(build_state()) == 4



def test_model_consensus():
    engine = AutonomousForecastAssistantEngine()

    assert engine.model_consensus(build_state()) == 85.0



def test_risk_assessment():
    engine = AutonomousForecastAssistantEngine()

    assert engine.risk_assessment(build_state()) == "HIGH"



def test_forecast_reliability():
    engine = AutonomousForecastAssistantEngine()

    assert engine.forecast_reliability(build_state()) == 82.5



def test_assistant_decision():
    engine = AutonomousForecastAssistantEngine()

    assert (
        engine.assistant_decision(build_state())
        == "GENERATE_WEATHER_WARNING"
    )



def test_summary():
    engine = AutonomousForecastAssistantEngine()

    result = engine.generate_summary(build_state())

    assert result["region"] == "Algeria"
    assert result["models_used"] == 4
