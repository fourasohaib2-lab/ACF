from acf.model4d.physics.natural_language_weather_intelligence_engine import (
    NaturalLanguageWeatherIntelligenceEngine,
    NaturalLanguageWeatherState,
)


def build_state():
    return NaturalLanguageWeatherState(
        region="Algeria",
        dominant_weather="stormy conditions",
        hazard_probability=82,
        confidence=85,
        models_agreement=90,
        temperature_trend="warming",
        precipitation_signal="strong",
    )


def test_hazard_level():
    engine = NaturalLanguageWeatherIntelligenceEngine()

    assert engine.hazard_level(build_state()) == "EXTREME"



def test_confidence_level():
    engine = NaturalLanguageWeatherIntelligenceEngine()

    assert engine.confidence_level(build_state()) == "HIGH"



def test_model_interpretation():
    engine = NaturalLanguageWeatherIntelligenceEngine()

    assert (
        engine.model_interpretation(build_state())
        ==
        "Les modèles numériques présentent une forte convergence."
    )



def test_generate_weather_explanation():
    engine = NaturalLanguageWeatherIntelligenceEngine()

    result = engine.generate_weather_explanation(build_state())

    assert "Algeria" in result
    assert "EXTREME" in result



def test_bulletin_summary():
    engine = NaturalLanguageWeatherIntelligenceEngine()

    result = engine.bulletin_summary(build_state())

    assert result["region"] == "Algeria"
    assert result["hazard_level"] == "EXTREME"
