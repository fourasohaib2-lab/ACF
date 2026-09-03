"""
Tests for acf.awci.theta_e - real per-point equivalent potential
temperature (docs/ACF_MASTER_PROMPT.md section 13, explicit user
request "continue au module thermodynamique, avec theta-e"). This
session's exhaustive 90-section conformance audit
(reports/ACF_MASTER_AUDIT_v2.md) found the real, published Bolton
(1980) formula already existed in this codebase but was never wired
into anything that computes ACF's real outputs.
"""

from __future__ import annotations

import pytest

from acf.awci.theta_e import compute_real_theta_e_at_point
from acf.science.dewpoint import DewPoint
from acf.science.equivalent_potential_temperature import EquivalentPotentialTemperature
from acf.science.thermodynamics import Thermodynamics


def test_matches_a_direct_composition_of_the_three_real_formulas():
    """Real proof the wrapper is a genuine composition, not a
    reimplementation - reconstructs the same real chain by hand and
    compares."""
    temperature_k, specific_humidity, pressure_hpa = 303.0, 0.018, 1000.0

    result = compute_real_theta_e_at_point(temperature_k, specific_humidity, pressure_hpa)

    rh = Thermodynamics.calculate_relative_humidity(specific_humidity, pressure_hpa, temperature_k, is_kelvin=True)
    dewpoint_c = DewPoint.calculate(temperature_k - 273.15, rh)
    dewpoint_k = dewpoint_c + 273.15
    expected_theta_e = EquivalentPotentialTemperature.calculate_bolton_1980(temperature_k, dewpoint_k, pressure_hpa)

    assert result["theta_e_k"] == pytest.approx(expected_theta_e)
    assert result["relative_humidity_pct"] == pytest.approx(rh)
    assert result["dewpoint_k"] == pytest.approx(dewpoint_k)


def test_is_real_data_true_for_a_real_moist_case():
    result = compute_real_theta_e_at_point(temperature_k=303.0, specific_humidity=0.018, pressure_hpa=1000.0)
    assert result["is_real_data"] is True
    assert result["status"] == "REAL_THETA_E_BOLTON_1980"


def test_warm_moist_air_produces_a_real_theta_e_above_temperature():
    """A real, well-known physical property: theta-e always exceeds
    the real dry-bulb temperature for any real moist air (the moisture
    term is always a positive multiplicative factor >= 1)."""
    result = compute_real_theta_e_at_point(temperature_k=303.0, specific_humidity=0.018, pressure_hpa=1000.0)
    assert result["theta_e_k"] > 303.0


def test_cold_dry_air_still_produces_a_real_finite_theta_e():
    result = compute_real_theta_e_at_point(temperature_k=260.0, specific_humidity=0.0005, pressure_hpa=900.0)
    assert result["is_real_data"] is True
    assert result["theta_e_k"] is not None
    assert result["theta_e_k"] > 0.0


def test_zero_specific_humidity_is_honestly_not_computed():
    """Exactly zero specific humidity -> zero real relative humidity ->
    no real meaningful dewpoint - honestly None, never fabricated."""
    result = compute_real_theta_e_at_point(temperature_k=280.0, specific_humidity=0.0, pressure_hpa=1000.0)
    assert result["is_real_data"] is False
    assert result["theta_e_k"] is None
    assert result["relative_humidity_pct"] is None
    assert result["dewpoint_k"] is None
    assert "honest_limitation" in result


def test_higher_humidity_produces_a_real_higher_theta_e_all_else_equal():
    """Real physical monotonicity: more moisture at the same
    temperature/pressure must increase theta-e, never decrease it."""
    drier = compute_real_theta_e_at_point(temperature_k=295.0, specific_humidity=0.008, pressure_hpa=1000.0)
    moister = compute_real_theta_e_at_point(temperature_k=295.0, specific_humidity=0.015, pressure_hpa=1000.0)
    assert moister["theta_e_k"] > drier["theta_e_k"]
