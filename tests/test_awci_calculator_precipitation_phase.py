"""
Tests for AWCICalculator's real, opt-in precipitation-phase-severity
blend in the microphysical module (docs/ACF_MASTER_PROMPT.md section
15, candidate variable "hydrométéores"). This session's exhaustive
90-section conformance audit (reports/ACF_MASTER_AUDIT_v2.md) found
the microphysical module used only precipitation RATE before this.
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
    "precipitation": 8.0,
    "pressure": 1000.0,
    "altitude": 500.0,
    "confidence": 80.0,
    "temporal_change": 5.0,
}


def test_without_precipitation_phase_severity_microphysical_module_is_bit_identical_to_before():
    calc = AWCICalculator()
    scores = calc.calculate_module_scores(dict(_BASE_DATA))
    expected = Normalizer.normalize_precipitation(8.0)
    assert scores["microphysical"] == pytest.approx(expected)


def test_with_precipitation_phase_severity_microphysical_module_is_a_50_50_blend():
    calc = AWCICalculator()
    data = {**_BASE_DATA, "precipitation_phase_severity": 1.0}

    scores = calc.calculate_module_scores(data)

    expected = 0.5 * Normalizer.normalize_precipitation(8.0) + 0.5 * Normalizer.normalize_precipitation_phase_severity(1.0)
    assert scores["microphysical"] == pytest.approx(expected)


def test_precipitation_phase_severity_blends_rather_than_replaces_the_precipitation_rate():
    """The naive precipitation-rate score must still play a real role
    once precipitation_phase_severity is supplied - real proof it's a
    blend, not a replacement."""
    calc = AWCICalculator()
    precip_norm = Normalizer.normalize_precipitation(8.0)
    data = {**_BASE_DATA, "precipitation_phase_severity": 1.0}

    scores = calc.calculate_module_scores(data)

    assert scores["microphysical"] != pytest.approx(precip_norm)
    assert scores["microphysical"] != pytest.approx(Normalizer.normalize_precipitation_phase_severity(1.0))


def test_precipitation_phase_severity_changes_the_microphysical_score_relative_to_rate_alone():
    calc = AWCICalculator()
    without_phase = calc.calculate_module_scores(dict(_BASE_DATA))["microphysical"]
    with_phase = calc.calculate_module_scores({**_BASE_DATA, "precipitation_phase_severity": 0.9})["microphysical"]
    assert with_phase != without_phase


def test_only_microphysical_module_changes_other_modules_unaffected():
    calc = AWCICalculator()
    without_phase = calc.calculate_module_scores(dict(_BASE_DATA))
    with_phase = calc.calculate_module_scores({**_BASE_DATA, "precipitation_phase_severity": 0.5})

    for key in ("dynamic", "thermodynamic", "convective", "topographic", "temporal", "confidence"):
        assert with_phase[key] == without_phase[key]


def test_full_calculate_pipeline_still_produces_a_coherent_score_with_precipitation_phase_severity():
    calc = AWCICalculator()
    result = calc.calculate({**_BASE_DATA, "precipitation_phase_severity": 0.7})
    assert 0.0 <= result["awci"] <= 100.0
    assert result["level"] in {"Very Low", "Low", "Moderate", "High", "Very High", "Extreme"}


def test_precipitation_phase_severity_respects_climatology_when_both_are_supplied():
    calc = AWCICalculator()
    phase_climatology = [0.0, 0.2, 0.4, 0.5, 0.7, 0.9, 1.0]
    data = {
        **_BASE_DATA,
        "precipitation_phase_severity": 0.7,
        "climatology": {"precipitation_phase_severity": phase_climatology},
    }

    scores = calc.calculate_module_scores(data)

    precip_norm = Normalizer.normalize_precipitation(8.0)
    expected = 0.5 * precip_norm + 0.5 * Normalizer.normalize_percentile(0.7, phase_climatology)
    assert scores["microphysical"] == pytest.approx(expected)


def test_normalize_precipitation_phase_severity_is_an_identity_clamp():
    assert Normalizer.normalize_precipitation_phase_severity(0.5) == pytest.approx(0.5)
    assert Normalizer.normalize_precipitation_phase_severity(0.0) == 0.0
    assert Normalizer.normalize_precipitation_phase_severity(1.0) == 1.0
    assert Normalizer.normalize_precipitation_phase_severity(1.5) == 1.0  # clipped
    assert Normalizer.normalize_precipitation_phase_severity(-0.5) == 0.0  # clipped
