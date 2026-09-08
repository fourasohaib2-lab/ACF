"""
Tests for AWCICalculator's real, opt-in maximum-updraft-velocity blend
in the convective module (docs/ACF_MASTER_PROMPT.md section 14,
explicit user request "continue au module convectif, avec le sommet
des nuages"). This session's exhaustive 90-section conformance audit
(reports/ACF_MASTER_AUDIT_v2.md) found the convective module used only
the naive CAPE/CIN blend before this; no real, peer-reviewed
cloud-top-HEIGHT formula exists anywhere in this codebase, so the user
was asked directly and chose this real, well-established parcel-theory
proxy (acf.awci.updraft.compute_real_max_updraft_velocity(), w_max =
sqrt(2*CAPE)) instead.
"""

from __future__ import annotations

import pytest

from acf.awci.calculator import AWCICalculator
from acf.awci.normalizer import Normalizer

_BASE_DATA = {
    "temperature": 300.0,
    "specific_humidity": 0.01,
    "wind_speed": 10.0,
    "cape": 1500.0,
    "cin": -100.0,
    "precipitation": 5.0,
    "pressure": 1000.0,
    "altitude": 500.0,
    "confidence": 80.0,
    "temporal_change": 5.0,
}


def test_without_updraft_velocity_convective_module_is_bit_identical_to_before():
    calc = AWCICalculator()
    scores = calc.calculate_module_scores(dict(_BASE_DATA))
    expected = 0.7 * Normalizer.normalize_cape(1500.0) + 0.3 * Normalizer.normalize_cin(-100.0)
    assert scores["convective"] == pytest.approx(expected)


def test_with_updraft_velocity_convective_module_is_a_50_50_blend():
    calc = AWCICalculator()
    data = {**_BASE_DATA, "updraft_velocity": 40.0}

    scores = calc.calculate_module_scores(data)

    cape_cin_base = 0.7 * Normalizer.normalize_cape(1500.0) + 0.3 * Normalizer.normalize_cin(-100.0)
    expected = 0.5 * cape_cin_base + 0.5 * Normalizer.normalize_updraft_velocity(40.0)
    assert scores["convective"] == pytest.approx(expected)


def test_updraft_velocity_blends_rather_than_replaces_the_cape_cin_base():
    """The naive CAPE/CIN base must still play a real role once
    updraft_velocity is supplied - real proof it's a blend, not a
    replacement (unlike theta_e in the thermodynamic module)."""
    calc = AWCICalculator()
    cape_cin_base = 0.7 * Normalizer.normalize_cape(1500.0) + 0.3 * Normalizer.normalize_cin(-100.0)
    data = {**_BASE_DATA, "updraft_velocity": 40.0}

    scores = calc.calculate_module_scores(data)

    assert scores["convective"] != pytest.approx(cape_cin_base)
    assert scores["convective"] != pytest.approx(Normalizer.normalize_updraft_velocity(40.0))


def test_updraft_velocity_changes_the_convective_score_relative_to_the_naive_blend():
    calc = AWCICalculator()
    without_updraft = calc.calculate_module_scores(dict(_BASE_DATA))["convective"]
    with_updraft = calc.calculate_module_scores({**_BASE_DATA, "updraft_velocity": 55.0})["convective"]
    assert with_updraft != without_updraft


def test_only_convective_module_changes_other_modules_unaffected():
    calc = AWCICalculator()
    without_updraft = calc.calculate_module_scores(dict(_BASE_DATA))
    with_updraft = calc.calculate_module_scores({**_BASE_DATA, "updraft_velocity": 30.0})

    for key in ("dynamic", "thermodynamic", "microphysical", "topographic", "temporal", "confidence"):
        assert with_updraft[key] == without_updraft[key]


def test_full_calculate_pipeline_still_produces_a_coherent_score_with_updraft_velocity():
    calc = AWCICalculator()
    result = calc.calculate({**_BASE_DATA, "updraft_velocity": 45.0})
    assert 0.0 <= result["awci"] <= 100.0
    assert result["level"] in {"Very Low", "Low", "Moderate", "High", "Very High", "Extreme"}


def test_updraft_velocity_respects_climatology_when_both_are_supplied():
    calc = AWCICalculator()
    updraft_climatology = [5.0, 15.0, 25.0, 35.0, 45.0, 55.0, 65.0]
    data = {**_BASE_DATA, "updraft_velocity": 40.0, "climatology": {"updraft_velocity": updraft_climatology}}

    scores = calc.calculate_module_scores(data)

    cape_cin_base = 0.7 * Normalizer.normalize_cape(1500.0) + 0.3 * Normalizer.normalize_cin(-100.0)
    expected = 0.5 * cape_cin_base + 0.5 * Normalizer.normalize_percentile(40.0, updraft_climatology)
    assert scores["convective"] == pytest.approx(expected)


def test_normalize_updraft_velocity_envelope():
    assert Normalizer.normalize_updraft_velocity(35.0) == pytest.approx(0.5)  # 35/70
    assert Normalizer.normalize_updraft_velocity(0.0) == 0.0
    assert Normalizer.normalize_updraft_velocity(70.0) == 1.0
    assert Normalizer.normalize_updraft_velocity(100.0) == 1.0  # clipped
    assert Normalizer.normalize_updraft_velocity(-10.0) == 0.0  # clipped
