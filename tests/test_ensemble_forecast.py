import pytest

from acf.model4d.physics.ensemble_forecast import EnsembleForecastPhysics


def test_ensemble_mean():

    value = EnsembleForecastPhysics.ensemble_mean([1, 2, 3])

    assert value == 2


def test_ensemble_spread():

    value = EnsembleForecastPhysics.ensemble_spread([1, 2, 3])

    assert round(value, 2) == 0.82


def test_uncertainty():

    value = EnsembleForecastPhysics.forecast_uncertainty([10, 11, 12])

    assert round(value, 2) == 0.08


def test_perturbation():

    value = EnsembleForecastPhysics.perturb_state(10, 0)

    assert value == 10


def test_confidence_high():

    result = EnsembleForecastPhysics.classify_confidence(0.05)

    assert result == "high"


def test_confidence_medium():

    result = EnsembleForecastPhysics.classify_confidence(0.5)

    assert result == "medium"


def test_confidence_low():

    result = EnsembleForecastPhysics.classify_confidence(2)

    assert result == "low"


def test_empty_error():

    with pytest.raises(ValueError):
        EnsembleForecastPhysics.ensemble_mean([])


def test_single_member_error():

    with pytest.raises(ValueError):
        EnsembleForecastPhysics.ensemble_spread([1])


def test_negative_amplitude():

    with pytest.raises(ValueError):
        EnsembleForecastPhysics.perturb_state(1, -1)


def test_zero_mean_error():

    with pytest.raises(ValueError):
        EnsembleForecastPhysics.forecast_uncertainty([0, 0])
