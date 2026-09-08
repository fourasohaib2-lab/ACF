"""
Tests for AWCICalculator's real, opt-in mountain-wave-Froude-severity
blend in the topographic module (docs/ACF_MASTER_PROMPT.md section 16,
explicit user request "continue au module relief, avec le vent"). This
session's exhaustive 90-section conformance audit
(reports/ACF_MASTER_AUDIT_v2.md) found the topographic module used
only static altitude before this.
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
    "altitude": 1800.0,
    "confidence": 80.0,
    "temporal_change": 5.0,
}


def test_without_mountain_wave_froude_topographic_module_is_bit_identical_to_before():
    calc = AWCICalculator()
    scores = calc.calculate_module_scores(dict(_BASE_DATA))
    expected = Normalizer.normalize_topographic(1800.0)
    assert scores["topographic"] == pytest.approx(expected)


def test_with_mountain_wave_froude_topographic_module_is_a_50_50_blend():
    calc = AWCICalculator()
    data = {**_BASE_DATA, "mountain_wave_froude": 0.4}

    scores = calc.calculate_module_scores(data)

    expected = 0.5 * Normalizer.normalize_topographic(1800.0) + 0.5 * Normalizer.normalize_mountain_wave_severity(0.4)
    assert scores["topographic"] == pytest.approx(expected)


def test_mountain_wave_froude_blends_rather_than_replaces_altitude():
    """The naive altitude score must still play a real role once
    mountain_wave_froude is supplied - real proof it's a blend, not a
    replacement."""
    calc = AWCICalculator()
    altitude_norm = Normalizer.normalize_topographic(1800.0)
    data = {**_BASE_DATA, "mountain_wave_froude": 0.1}

    scores = calc.calculate_module_scores(data)

    assert scores["topographic"] != pytest.approx(altitude_norm)
    assert scores["topographic"] != pytest.approx(Normalizer.normalize_mountain_wave_severity(0.1))


def test_mountain_wave_froude_changes_the_topographic_score_relative_to_altitude_alone():
    calc = AWCICalculator()
    without_froude = calc.calculate_module_scores(dict(_BASE_DATA))["topographic"]
    with_froude = calc.calculate_module_scores({**_BASE_DATA, "mountain_wave_froude": 0.2})["topographic"]
    assert with_froude != without_froude


def test_only_topographic_module_changes_other_modules_unaffected():
    calc = AWCICalculator()
    without_froude = calc.calculate_module_scores(dict(_BASE_DATA))
    with_froude = calc.calculate_module_scores({**_BASE_DATA, "mountain_wave_froude": 0.6})

    for key in ("dynamic", "thermodynamic", "convective", "microphysical", "temporal", "confidence"):
        assert with_froude[key] == without_froude[key]


def test_full_calculate_pipeline_still_produces_a_coherent_score_with_mountain_wave_froude():
    calc = AWCICalculator()
    result = calc.calculate({**_BASE_DATA, "mountain_wave_froude": 0.3})
    assert 0.0 <= result["awci"] <= 100.0
    assert result["level"] in {"Very Low", "Low", "Moderate", "High", "Very High", "Extreme"}


def test_lower_froude_produces_higher_topographic_score_all_else_equal():
    """Real physical monotonicity: Fr closer to 0 (stronger blocking/
    wave hazard) must produce a higher topographic complexity score."""
    calc = AWCICalculator()
    low_fr = calc.calculate_module_scores({**_BASE_DATA, "mountain_wave_froude": 0.1})["topographic"]
    high_fr = calc.calculate_module_scores({**_BASE_DATA, "mountain_wave_froude": 0.9})["topographic"]
    assert low_fr > high_fr


def test_mountain_wave_froude_respects_climatology_when_both_are_supplied():
    calc = AWCICalculator()
    froude_climatology = [0.0, 0.2, 0.4, 0.5, 0.7, 0.9, 1.0]
    data = {
        **_BASE_DATA,
        "mountain_wave_froude": 0.4,
        "climatology": {"mountain_wave_froude": froude_climatology},
    }

    scores = calc.calculate_module_scores(data)

    altitude_norm = Normalizer.normalize_topographic(1800.0)
    expected = 0.5 * altitude_norm + 0.5 * Normalizer.normalize_percentile(0.4, froude_climatology)
    assert scores["topographic"] == pytest.approx(expected)


def test_normalize_mountain_wave_severity_envelope():
    assert Normalizer.normalize_mountain_wave_severity(0.0) == pytest.approx(1.0)  # maximum blocking hazard
    assert Normalizer.normalize_mountain_wave_severity(1.0) == pytest.approx(0.0)  # neutral threshold
    assert Normalizer.normalize_mountain_wave_severity(0.5) == pytest.approx(0.5)
    assert Normalizer.normalize_mountain_wave_severity(2.0) == 0.0  # clipped
    assert Normalizer.normalize_mountain_wave_severity(-0.5) == 1.0  # clipped
