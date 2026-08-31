from acf.model4d.physics.advanced_ensemble_forecast_engine import (
    AdvancedEnsembleForecastEngine,
    AdvancedEnsembleForecastState,
)


def build_state():
    return AdvancedEnsembleForecastState(
        arpege=82,
        arome=88,
        wrf=79,
        icon=84,
        ecmwf=91,
        model_agreement=88,
        observation_support=92,
        atmospheric_predictability=85,
    )


def test_ensemble_mean():
    engine = AdvancedEnsembleForecastEngine()

    result = engine.ensemble_mean(build_state())

    assert result > 0


def test_ensemble_spread():
    engine = AdvancedEnsembleForecastEngine()

    result = engine.ensemble_spread(build_state())

    assert result >= 0


def test_uncertainty_index():
    engine = AdvancedEnsembleForecastEngine()

    result = engine.uncertainty_index(build_state())

    assert result >= 0


def test_confidence_score():
    engine = AdvancedEnsembleForecastEngine()

    result = engine.confidence_score(build_state())

    assert result == 88.33


def test_probabilistic_forecast_index():
    engine = AdvancedEnsembleForecastEngine()

    result = engine.probabilistic_forecast_index(build_state())

    assert result > 0


def test_best_model():
    engine = AdvancedEnsembleForecastEngine()

    result = engine.best_model(build_state())

    assert result == "ECMWF"


def test_model4d_ready():
    engine = AdvancedEnsembleForecastEngine()

    assert engine.model4d_ready(build_state()) is True


def test_ensemble_update():
    engine = AdvancedEnsembleForecastEngine()

    result = engine.ensemble_update(build_state())

    assert "ensemble_mean" in result
    assert "confidence" in result
    assert "best_model" in result


def test_state_values():
    state = build_state()

    assert state.arpege == 82
    assert state.ecmwf == 91


def test_engine_creation():
    engine = AdvancedEnsembleForecastEngine()

    assert engine is not None
