from acf.model4d.physics.probabilistic_extreme_weather_intelligence_engine import (
    ProbabilisticExtremeWeatherIntelligenceEngine,
    ExtremeWeatherIntelligenceState,
)


def build_state():
    return ExtremeWeatherIntelligenceState(
        ensemble_mean=85,
        uncertainty=10,
        confidence=90,

        temperature_anomaly=75,
        precipitation_anomaly=85,
        wind_anomaly=65,
        convection_index=80,
    )


def test_hazard_probability():
    engine = ProbabilisticExtremeWeatherIntelligenceEngine()

    result = engine.hazard_probability(build_state())

    assert result == 76.25


def test_uncertainty_penalty():
    engine = ProbabilisticExtremeWeatherIntelligenceEngine()

    result = engine.uncertainty_penalty(build_state())

    assert result == 3.5


def test_corrected_hazard_index():
    engine = ProbabilisticExtremeWeatherIntelligenceEngine()

    result = engine.corrected_hazard_index(build_state())

    assert result == 72.75


def test_risk_level():
    engine = ProbabilisticExtremeWeatherIntelligenceEngine()

    result = engine.risk_level(build_state())

    assert result == "HIGH"


def test_alert_level():
    engine = ProbabilisticExtremeWeatherIntelligenceEngine()

    result = engine.alert_level(build_state())

    assert result == 3


def test_model4d_ready():
    engine = ProbabilisticExtremeWeatherIntelligenceEngine()

    result = engine.model4d_ready(build_state())

    assert result is True


def test_intelligence_update_keys():
    engine = ProbabilisticExtremeWeatherIntelligenceEngine()

    result = engine.intelligence_update(build_state())

    assert "hazard_probability" in result
    assert "hazard_index" in result
    assert "risk_level" in result
    assert "alert_level" in result


def test_state_values():
    state = build_state()

    assert state.temperature_anomaly == 75
    assert state.precipitation_anomaly == 85
    assert state.convection_index == 80


def test_engine_creation():
    engine = ProbabilisticExtremeWeatherIntelligenceEngine()

    assert engine is not None


def test_low_risk_scenario():
    engine = ProbabilisticExtremeWeatherIntelligenceEngine()

    state = ExtremeWeatherIntelligenceState(
        ensemble_mean=40,
        uncertainty=5,
        confidence=80,

        temperature_anomaly=10,
        precipitation_anomaly=15,
        wind_anomaly=20,
        convection_index=10,
    )

    assert engine.risk_level(state) == "LOW"
