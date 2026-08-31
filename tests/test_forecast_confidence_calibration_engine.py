from acf.model4d.physics.forecast_confidence_calibration_engine import (
    ForecastConfidenceCalibrationEngine,
    ForecastConfidenceCalibrationState,
)


def build_state():

    return ForecastConfidenceCalibrationState(
        forecast_error=10,
        observation_error=15,
        model_confidence=85,
        assimilation_quality=90,
        historical_accuracy=88,
        learning_factor=2,
    )


def test_raw_confidence():

    engine = ForecastConfidenceCalibrationEngine()

    assert engine.raw_confidence(build_state()) == 87.0


def test_error_correction():

    engine = ForecastConfidenceCalibrationEngine()

    assert engine.error_correction_index(build_state()) == 87.5


def test_bias():

    engine = ForecastConfidenceCalibrationEngine()

    result = engine.confidence_bias(build_state())

    assert round(result, 2) == -2.75


def test_adjustment():

    engine = ForecastConfidenceCalibrationEngine()

    result = engine.confidence_adjustment(build_state())

    assert round(result, 2) == 89.78


def test_calibrated():

    engine = ForecastConfidenceCalibrationEngine()

    result = engine.calibrated_confidence(build_state())

    assert round(result, 2) == 96.12


def test_operational():

    engine = ForecastConfidenceCalibrationEngine()

    result = engine.operational_confidence(build_state())

    assert round(result, 2) == 91.88


def test_level():

    engine = ForecastConfidenceCalibrationEngine()

    assert engine.confidence_level(build_state()) == "VERY_HIGH"


def test_update():

    engine = ForecastConfidenceCalibrationEngine()

    result = engine.confidence_update(build_state())

    assert result["confidence_level"] == "VERY_HIGH"
