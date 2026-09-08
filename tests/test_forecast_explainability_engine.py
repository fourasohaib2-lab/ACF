from acf.model4d.physics.forecast_explainability_engine import (
    ForecastExplainabilityEngine,
    ForecastExplainabilityState,
)


def build_state():

    return ForecastExplainabilityState(
        hazard_index=82.5,
        confidence=91.0,
        decision="ISSUE_WEATHER_WARNING",
        causes=[
            "HIGH_CAPE",
            "LOW_LEVEL_HUMIDITY",
            "UPPER_FORCING",
        ],
        recommended_action="Issue official weather warning",
    )


def test_scientific_explanation():

    engine = ForecastExplainabilityEngine()

    result = engine.scientific_explanation(build_state())

    assert "ISSUE_WEATHER_WARNING" in result

    assert "82.50" in result

    assert "91.00" in result


def test_human_explanation():

    engine = ForecastExplainabilityEngine()

    result = engine.human_explanation(build_state())

    assert result == "Hazardous weather conditions are expected."


def test_confidence_comment():

    engine = ForecastExplainabilityEngine()

    result = engine.confidence_comment(build_state())

    assert result == "Forecast confidence is high."


def test_operational_summary():

    engine = ForecastExplainabilityEngine()

    result = engine.operational_summary(build_state())

    assert "Decision:" in result

    assert "Recommended Action:" in result

    assert "HIGH_CAPE" in result


def test_full_explanation():

    engine = ForecastExplainabilityEngine()

    result = engine.full_explanation(build_state())

    assert result["decision"] == "ISSUE_WEATHER_WARNING"

    assert result["recommended_action"] == "Issue official weather warning"

    assert len(result["causes"]) == 3


def test_export_report():

    engine = ForecastExplainabilityEngine()

    result = engine.export_report(build_state())

    assert "Forecast Explainability" in result

    assert "Scientific Explanation" in result

    assert "Human Explanation" in result
