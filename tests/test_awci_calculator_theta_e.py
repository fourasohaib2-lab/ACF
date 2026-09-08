"""
Tests for AWCICalculator's real, opt-in theta-e replacement of the
thermodynamic module (docs/ACF_MASTER_PROMPT.md section 13, explicit
user request "continue au module thermodynamique, avec theta-e"). This
session's exhaustive 90-section conformance audit
(reports/ACF_MASTER_AUDIT_v2.md) found the thermodynamic module used
only a naive temperature/humidity blend before this.
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


def test_without_theta_e_thermodynamic_module_is_bit_identical_to_before():
    calc = AWCICalculator()
    scores = calc.calculate_module_scores(dict(_BASE_DATA))
    expected = 0.5 * Normalizer.normalize_temperature(300.0) + 0.5 * Normalizer.normalize_humidity(0.01)
    assert scores["thermodynamic"] == pytest.approx(expected)


def test_with_theta_e_thermodynamic_module_uses_theta_e_alone():
    calc = AWCICalculator()
    data = {**_BASE_DATA, "theta_e": 330.0}

    scores = calc.calculate_module_scores(data)

    expected = Normalizer.normalize_theta_e(330.0)
    assert scores["thermodynamic"] == pytest.approx(expected)


def test_theta_e_replaces_rather_than_blends_with_the_naive_combination():
    """The naive temperature/humidity blend must play NO role at all
    once theta_e is supplied - real proof it's a replacement, not a
    3-way average."""
    calc = AWCICalculator()
    naive_blend = 0.5 * Normalizer.normalize_temperature(300.0) + 0.5 * Normalizer.normalize_humidity(0.01)
    data = {**_BASE_DATA, "theta_e": 330.0}

    scores = calc.calculate_module_scores(data)

    assert scores["thermodynamic"] != pytest.approx(naive_blend)
    assert scores["thermodynamic"] == pytest.approx(Normalizer.normalize_theta_e(330.0))


def test_theta_e_changes_the_thermodynamic_score_relative_to_the_naive_blend():
    calc = AWCICalculator()
    without_theta_e = calc.calculate_module_scores(dict(_BASE_DATA))["thermodynamic"]
    with_theta_e = calc.calculate_module_scores({**_BASE_DATA, "theta_e": 355.0})["thermodynamic"]
    assert with_theta_e != without_theta_e


def test_only_thermodynamic_module_changes_other_modules_unaffected():
    calc = AWCICalculator()
    without_theta_e = calc.calculate_module_scores(dict(_BASE_DATA))
    with_theta_e = calc.calculate_module_scores({**_BASE_DATA, "theta_e": 340.0})

    for key in ("dynamic", "convective", "microphysical", "topographic", "temporal", "confidence"):
        assert with_theta_e[key] == without_theta_e[key]


def test_full_calculate_pipeline_still_produces_a_coherent_score_with_theta_e():
    calc = AWCICalculator()
    result = calc.calculate({**_BASE_DATA, "theta_e": 345.0})
    assert 0.0 <= result["awci"] <= 100.0
    assert result["level"] in {"Very Low", "Low", "Moderate", "High", "Very High", "Extreme"}


def test_theta_e_respects_climatology_when_both_are_supplied():
    calc = AWCICalculator()
    theta_e_climatology = [280.0, 300.0, 315.0, 325.0, 335.0, 350.0, 365.0]
    data = {**_BASE_DATA, "theta_e": 330.0, "climatology": {"theta_e": theta_e_climatology}}

    scores = calc.calculate_module_scores(data)

    expected = Normalizer.normalize_percentile(330.0, theta_e_climatology)
    assert scores["thermodynamic"] == pytest.approx(expected)


def test_normalize_theta_e_envelope():
    assert Normalizer.normalize_theta_e(315.0) == pytest.approx(0.5)  # (315-250)/130
    assert Normalizer.normalize_theta_e(250.0) == 0.0
    assert Normalizer.normalize_theta_e(380.0) == 1.0
    assert Normalizer.normalize_theta_e(400.0) == 1.0  # clipped
    assert Normalizer.normalize_theta_e(200.0) == 0.0  # clipped
