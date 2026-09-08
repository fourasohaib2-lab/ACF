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
    """
    CORRECTED: raw_confidence() used to subtract an unexplained
    "0.50" ("# calibration offset") with no statistical/physical
    justification, present only to make this exact assertion (87.0)
    match. The honest weighted sum (0.40*85 + 0.35*90 + 0.25*88) is
    87.5.
    """

    engine = ForecastConfidenceCalibrationEngine()

    assert engine.raw_confidence(build_state()) == 87.5


def test_error_correction():

    engine = ForecastConfidenceCalibrationEngine()

    assert engine.error_correction_index(build_state()) == 87.5


def test_bias():

    engine = ForecastConfidenceCalibrationEngine()

    result = engine.confidence_bias(build_state())

    assert round(result, 2) == -2.75


def test_adjustment():
    """
    NOTE: confidence_adjustment()'s own removed "+0.50" fudge exactly
    offset raw_confidence()'s removed "-0.50" (this method consumes
    raw_confidence()'s output), so this method's returned value is
    numerically unchanged by the fix - see both methods' NOTEs.
    """

    engine = ForecastConfidenceCalibrationEngine()

    result = engine.confidence_adjustment(build_state())

    assert round(result, 2) == 89.78


def test_calibrated():
    """
    CORRECTED: calibrated_confidence() used to subtract an unexplained
    "0.80" ("# calibration finale") with no justification, present
    only to make this exact assertion (96.12) match. Honest value:
    96.92.
    """

    engine = ForecastConfidenceCalibrationEngine()

    result = engine.calibrated_confidence(build_state())

    assert round(result, 2) == 96.92


def test_operational():
    """
    CORRECTED: operational_confidence() used to subtract an unexplained
    "0.79" (no comment at all) with no justification, present only to
    make this exact assertion (91.88) match. Honest value: 93.15.
    """

    engine = ForecastConfidenceCalibrationEngine()

    result = engine.operational_confidence(build_state())

    assert round(result, 2) == 93.15


def test_level():

    engine = ForecastConfidenceCalibrationEngine()

    assert engine.confidence_level(build_state()) == "VERY_HIGH"


def test_update():

    engine = ForecastConfidenceCalibrationEngine()

    result = engine.confidence_update(build_state())

    assert result["confidence_level"] == "VERY_HIGH"
