"""
Tests for AWCICalculator's real, opt-in `microburst` module
(post-model4d audit, 2026-09-11) - connecting the already-real,
already-cited acf.aviation.hazards.aviation_hazards
"microburst_windshear" encyclopedia entry to a live diagnostic. Same
"keep the dashboard bit-identical by default" discipline as
test_awci_calculator_ceiling_visibility.py.
"""

from __future__ import annotations

import pytest

from acf.awci.calculator import AWCICalculator
from acf.awci.normalizer import Normalizer
from acf.awci.weights import WeightsManager

_BASE_DATA = {
    "temperature": 300.0,
    "specific_humidity": 0.01,
    "wind_speed": 10.0,
    "cape": 1000.0,
    "cin": -100.0,
    "precipitation": 5.0,
    "pressure": 1000.0,
    "altitude": 500.0,
    "confidence": 80.0,
    "temporal_change": 5.0,
}


def test_default_weight_is_zero():
    assert WeightsManager.DEFAULT_WEIGHTS["microburst"] == 0.0
    WeightsManager()  # raises ValueError if the sum drifted off 1.0


def test_omitting_the_key_gives_a_bit_identical_awci_to_before_this_module_existed():
    calc = AWCICalculator()
    scores = calc.calculate_module_scores(dict(_BASE_DATA))
    result = calc.calculate(dict(_BASE_DATA))

    assert scores["microburst"] == 0.0
    assert result["decomposition"]["microburst"] == 0.0


def test_supplying_microburst_risk_activates_the_real_normalize_value():
    calc = AWCICalculator()
    data = {**_BASE_DATA, "microburst_risk": 0.8}

    scores = calc.calculate_module_scores(data)

    assert scores["microburst"] == pytest.approx(Normalizer.normalize_microburst_risk(0.8))
    assert scores["microburst"] == pytest.approx(0.8)


def test_opted_in_microburst_only_contributes_when_its_weight_is_explicitly_raised():
    calc = AWCICalculator()
    data = {**_BASE_DATA, "microburst_risk": 1.0}

    default_weight_result = calc.calculate(data)
    assert default_weight_result["decomposition"]["microburst"] == 0.0

    weights = WeightsManager()
    weights.update_weights({"microburst": 0.20, "dynamic": 0.0})
    calc_weighted = AWCICalculator(weights=weights.get_all_weights())
    weighted_result = calc_weighted.calculate(data)
    assert weighted_result["decomposition"]["microburst"] > 0.0


def test_microburst_is_classified_as_a_physical_module():
    assert "microburst" in AWCICalculator.PHYSICAL_MODULES
    assert "microburst" not in AWCICalculator.FORECAST_MODULES


def test_physical_and_forecast_modules_still_partition_all_modules():
    calc = AWCICalculator()
    all_modules = set(calc.calculate_module_scores({}).keys())
    assert AWCICalculator.PHYSICAL_MODULES | AWCICalculator.FORECAST_MODULES == all_modules
    assert AWCICalculator.PHYSICAL_MODULES.isdisjoint(AWCICalculator.FORECAST_MODULES)
