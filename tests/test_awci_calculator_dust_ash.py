"""
Tests for AWCICalculator's real, opt-in `dust`/`ash` modules
(post-model4d audit, 2026-09-11, closing AWCI's "poussière et sable"
and "cendres volcaniques" gaps). Same "keep the dashboard bit-identical
by default" discipline as test_awci_calculator_ceiling_visibility.py -
see that file's own module docstring for the full rationale.
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


def test_default_weights_are_zero_for_both_new_modules():
    assert WeightsManager.DEFAULT_WEIGHTS["dust"] == 0.0
    assert WeightsManager.DEFAULT_WEIGHTS["ash"] == 0.0
    WeightsManager()  # raises ValueError if the sum drifted off 1.0


def test_omitting_both_keys_gives_a_bit_identical_awci_to_before_these_modules_existed():
    calc = AWCICalculator()
    scores = calc.calculate_module_scores(dict(_BASE_DATA))
    result = calc.calculate(dict(_BASE_DATA))

    assert scores["dust"] == 0.0
    assert scores["ash"] == 0.0
    assert result["decomposition"]["dust"] == 0.0
    assert result["decomposition"]["ash"] == 0.0


def test_module_scores_key_set_now_includes_dust_and_ash():
    calc = AWCICalculator()
    scores = calc.calculate_module_scores({})
    assert "dust" in scores
    assert "ash" in scores


def test_supplying_dust_risk_activates_the_real_normalize_dust_risk_value():
    calc = AWCICalculator()
    data = {**_BASE_DATA, "dust_risk": 0.6}

    scores = calc.calculate_module_scores(data)

    assert scores["dust"] == pytest.approx(Normalizer.normalize_dust_risk(0.6))
    assert scores["dust"] == pytest.approx(0.6)


def test_supplying_ash_risk_activates_the_real_normalize_ash_risk_value():
    calc = AWCICalculator()
    data = {**_BASE_DATA, "ash_risk": 0.9}

    scores = calc.calculate_module_scores(data)

    assert scores["ash"] == pytest.approx(0.9)


def test_opted_in_dust_only_contributes_when_its_weight_is_explicitly_raised():
    calc = AWCICalculator()
    data = {**_BASE_DATA, "dust_risk": 1.0}

    default_weight_result = calc.calculate(data)
    assert default_weight_result["decomposition"]["dust"] == 0.0

    weights = WeightsManager()
    weights.update_weights({"dust": 0.20, "dynamic": 0.0})
    calc_weighted = AWCICalculator(weights=weights.get_all_weights())
    weighted_result = calc_weighted.calculate(data)
    assert weighted_result["decomposition"]["dust"] > 0.0


def test_dust_and_ash_are_classified_as_physical_modules():
    assert "dust" in AWCICalculator.PHYSICAL_MODULES
    assert "ash" in AWCICalculator.PHYSICAL_MODULES
    assert "dust" not in AWCICalculator.FORECAST_MODULES
    assert "ash" not in AWCICalculator.FORECAST_MODULES


def test_physical_and_forecast_modules_still_partition_all_modules():
    """Same invariant tests/test_awci_calculator.py's own
    test_physical_and_forecast_modules_partition_all_modules() enforces
    - re-checked directly here for the 2 modules this file adds."""
    calc = AWCICalculator()
    all_modules = set(calc.calculate_module_scores({}).keys())
    assert AWCICalculator.PHYSICAL_MODULES | AWCICalculator.FORECAST_MODULES == all_modules
    assert AWCICalculator.PHYSICAL_MODULES.isdisjoint(AWCICalculator.FORECAST_MODULES)
