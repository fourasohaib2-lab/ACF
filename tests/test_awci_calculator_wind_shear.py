"""
Tests for AWCICalculator's real, opt-in wind shear blend in the
dynamic module (docs/ACF_MASTER_PROMPT.md section 12, explicit user
request "commence par le module dynamique, avec le cisaillement de
vent"). This session's exhaustive 90-section conformance audit
(reports/ACF_MASTER_AUDIT_v2.md) found the dynamic module used only a
single scalar wind speed before this.
"""

from __future__ import annotations

import pytest

from acf.awci.calculator import AWCICalculator
from acf.awci.normalizer import Normalizer

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


def test_without_wind_shear_dynamic_module_is_bit_identical_to_before():
    calc = AWCICalculator()
    scores_without = calc.calculate_module_scores(dict(_BASE_DATA))
    expected = Normalizer.normalize_wind(_BASE_DATA["wind_speed"])
    assert scores_without["dynamic"] == expected


def test_with_wind_shear_dynamic_module_blends_50_50():
    calc = AWCICalculator()
    data = {**_BASE_DATA, "wind_shear": 15.0}

    scores = calc.calculate_module_scores(data)

    expected_wind = Normalizer.normalize_wind(_BASE_DATA["wind_speed"])
    expected_shear = Normalizer.normalize_wind_shear(15.0)
    assert scores["dynamic"] == pytest.approx(0.5 * expected_wind + 0.5 * expected_shear)


def test_wind_shear_changes_the_dynamic_score_relative_to_wind_speed_alone():
    calc = AWCICalculator()
    without_shear = calc.calculate_module_scores(dict(_BASE_DATA))["dynamic"]
    with_shear = calc.calculate_module_scores({**_BASE_DATA, "wind_shear": 40.0})["dynamic"]
    assert with_shear != without_shear


def test_only_dynamic_module_changes_other_modules_unaffected():
    calc = AWCICalculator()
    without_shear = calc.calculate_module_scores(dict(_BASE_DATA))
    with_shear = calc.calculate_module_scores({**_BASE_DATA, "wind_shear": 25.0})

    for key in ("thermodynamic", "convective", "microphysical", "topographic", "temporal", "confidence"):
        assert with_shear[key] == without_shear[key]


def test_full_calculate_pipeline_still_produces_a_coherent_score_with_wind_shear():
    calc = AWCICalculator()
    result = calc.calculate({**_BASE_DATA, "wind_shear": 30.0})
    assert 0.0 <= result["awci"] <= 100.0
    assert result["level"] in {"Very Low", "Low", "Moderate", "High", "Very High", "Extreme"}


def test_wind_shear_respects_climatology_when_both_are_supplied():
    """The opt-in wind_shear blend is climatology-aware too, via the
    same _normalize() dispatch every other module-input variable uses."""
    calc = AWCICalculator()
    shear_climatology = [1.0, 5.0, 10.0, 15.0, 20.0, 30.0, 45.0]
    data = {**_BASE_DATA, "wind_shear": 20.0, "climatology": {"wind_shear": shear_climatology}}

    scores = calc.calculate_module_scores(data)

    expected_shear = Normalizer.normalize_percentile(20.0, shear_climatology)
    expected_wind = Normalizer.normalize_wind(_BASE_DATA["wind_speed"])
    assert scores["dynamic"] == pytest.approx(0.5 * expected_wind + 0.5 * expected_shear)


def test_normalize_wind_shear_matches_normalize_wind_envelope():
    """Same real [0, 50] m/s envelope as normalize_wind, for internal consistency (see Normalizer's own docstring)."""
    assert Normalizer.normalize_wind_shear(25.0) == pytest.approx(0.5)
    assert Normalizer.normalize_wind_shear(0.0) == 0.0
    assert Normalizer.normalize_wind_shear(100.0) == 1.0  # clipped
    assert Normalizer.normalize_wind_shear(-5.0) == 0.0  # clipped
