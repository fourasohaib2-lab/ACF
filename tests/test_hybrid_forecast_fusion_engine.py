from acf.model4d.physics.hybrid_forecast_fusion_engine import (
    HybridForecastFusionEngine,
    HybridForecastFusionState,
)


def build_state():
    return HybridForecastFusionState(
        arpege=82,
        arome=88,
        wrf=79,
        icon=84,
        ecmwf=91,

        arpege_quality=90,
        arome_quality=92,
        wrf_quality=88,
        icon_quality=91,
        ecmwf_quality=95,

        forecast_consistency=87,
        observation_quality=92,
        atmosphere_stability=85,
    )


def test_arpege_weight():
    engine = HybridForecastFusionEngine()
    assert engine.arpege_weight(build_state()) > 0


def test_arome_weight():
    engine = HybridForecastFusionEngine()
    assert engine.arome_weight(build_state()) > 0


def test_wrf_weight():
    engine = HybridForecastFusionEngine()
    assert engine.wrf_weight(build_state()) > 0


def test_icon_weight():
    engine = HybridForecastFusionEngine()
    assert engine.icon_weight(build_state()) > 0


def test_ecmwf_weight():
    engine = HybridForecastFusionEngine()
    assert engine.ecmwf_weight(build_state()) > 0


def test_average_weight():
    engine = HybridForecastFusionEngine()
    result = engine.average_weight(build_state())
    assert result > 0


def test_hybrid_forecast():
    engine = HybridForecastFusionEngine()
    result = engine.hybrid_forecast(build_state())
    assert result > 0


def test_confidence():
    engine = HybridForecastFusionEngine()
    result = engine.confidence_score(build_state())
    assert result > 0


def test_best_model():
    engine = HybridForecastFusionEngine()
    assert engine.best_model(build_state()) == "ECMWF"


def test_model4d_ready():
    engine = HybridForecastFusionEngine()
    assert engine.model4d_ready(build_state()) is True
