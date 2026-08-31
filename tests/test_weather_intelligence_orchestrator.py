from acf.model4d.physics.weather_intelligence_orchestrator import (
    WeatherIntelligenceInput,
    WeatherIntelligenceOrchestrator,
)


def build_state():

    return WeatherIntelligenceInput(
        region="Algeria",
        models=[
            "ARPEGE",
            "AROME",
            "WRF",
            "ICON",
        ],
        observation_score=90,
        ensemble_score=85,
        hazard_probability=75,
        confidence=80,
        uncertainty=10,
        weather_description="Heavy convective storms expected",
    )


def test_active_models():

    engine = WeatherIntelligenceOrchestrator()

    assert engine.active_models(build_state()) == 4


def test_observation_quality():

    engine = WeatherIntelligenceOrchestrator()

    assert engine.observation_quality(build_state()) == 90


def test_ensemble_quality():

    engine = WeatherIntelligenceOrchestrator()

    assert engine.ensemble_quality(build_state()) == 85


def test_risk_level():

    engine = WeatherIntelligenceOrchestrator()

    assert engine.risk_level(build_state()) == "HIGH"


def test_confidence():

    engine = WeatherIntelligenceOrchestrator()

    assert engine.forecast_confidence(build_state()) == 81.67


def test_decision():

    engine = WeatherIntelligenceOrchestrator()

    assert engine.operational_decision(build_state()) == "WEATHER_WARNING"


def test_report():

    engine = WeatherIntelligenceOrchestrator()

    result = engine.generate_intelligence_report(build_state())

    assert result["region"] == "Algeria"
    assert result["models_used"] == 4
    assert result["risk_level"] == "HIGH"
