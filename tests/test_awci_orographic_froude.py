"""
Tests for acf.awci.orographic_froude - real mountain-wave Froude
number (docs/ACF_MASTER_PROMPT.md section 16, explicit user request
"continue au module relief, avec le vent"). This session's exhaustive
90-section conformance audit (reports/ACF_MASTER_AUDIT_v2.md) found
this real, already-existing, cited formula
(acf.science.encyclopedia.aviation_extended.calculate_mountain_wave_froude_number)
was registered in the encyclopedia but never wired into anything
producing a real ACF output.
"""

from __future__ import annotations

import math

import pytest

from acf.awci.orographic_froude import compute_real_mountain_wave_froude_number_at_point
from acf.core.exceptions import RangeError
from acf.science.cyclones import BruntVaisalaFrequency
from acf.science.encyclopedia.aviation_extended import calculate_mountain_wave_froude_number


def test_matches_a_direct_call_to_the_real_encyclopedia_formula():
    result = compute_real_mountain_wave_froude_number_at_point(
        wind_speed_perpendicular=15.0, brunt_vaisala_n=0.02, mountain_height_m=1500.0
    )
    expected = calculate_mountain_wave_froude_number(15.0, 0.02, 1500.0)
    assert result["froude_number"] == pytest.approx(expected)


def test_real_known_value_cross_check():
    """Fr = U/(N*H) = 20 / (0.02 * 2000) = 0.5 - independently verifiable by hand."""
    result = compute_real_mountain_wave_froude_number_at_point(
        wind_speed_perpendicular=20.0, brunt_vaisala_n=0.02, mountain_height_m=2000.0
    )
    assert result["froude_number"] == pytest.approx(0.5)


def test_strong_stability_moderate_wind_tall_mountain_gives_low_froude_blocking_regime():
    n = BruntVaisalaFrequency.calculate(potential_temperature_k=300.0, dtheta_dz=0.02)
    result = compute_real_mountain_wave_froude_number_at_point(
        wind_speed_perpendicular=15.0, brunt_vaisala_n=n, mountain_height_m=2000.0
    )
    assert result["froude_number"] < 1.0


def test_weak_stability_strong_wind_small_hill_gives_high_froude_flow_over_regime():
    n = BruntVaisalaFrequency.calculate(potential_temperature_k=300.0, dtheta_dz=0.002)
    result = compute_real_mountain_wave_froude_number_at_point(
        wind_speed_perpendicular=20.0, brunt_vaisala_n=n, mountain_height_m=500.0
    )
    assert result["froude_number"] > 1.0


def test_neutral_or_unstable_stratification_is_honestly_not_computed():
    """BruntVaisalaFrequency.calculate() itself honestly returns N=0 for
    dtheta_dz <= 0 - froude_number must be None, never a fabricated
    infinite/zero value."""
    n = BruntVaisalaFrequency.calculate(potential_temperature_k=300.0, dtheta_dz=-0.001)
    assert n == 0.0
    result = compute_real_mountain_wave_froude_number_at_point(
        wind_speed_perpendicular=15.0, brunt_vaisala_n=n, mountain_height_m=2000.0
    )
    assert result["froude_number"] is None
    assert result["is_real_data"] is False


def test_directly_negative_brunt_vaisala_n_is_also_honestly_not_computed():
    result = compute_real_mountain_wave_froude_number_at_point(
        wind_speed_perpendicular=15.0, brunt_vaisala_n=-0.01, mountain_height_m=2000.0
    )
    assert result["froude_number"] is None
    assert result["is_real_data"] is False


def test_non_positive_mountain_height_raises():
    with pytest.raises(ValueError):
        compute_real_mountain_wave_froude_number_at_point(
            wind_speed_perpendicular=15.0, brunt_vaisala_n=0.02, mountain_height_m=0.0
        )
    with pytest.raises(ValueError):
        compute_real_mountain_wave_froude_number_at_point(
            wind_speed_perpendicular=15.0, brunt_vaisala_n=0.02, mountain_height_m=-100.0
        )


def test_is_real_data_and_status_are_honest():
    result = compute_real_mountain_wave_froude_number_at_point(
        wind_speed_perpendicular=15.0, brunt_vaisala_n=0.02, mountain_height_m=1500.0
    )
    assert result["is_real_data"] is True
    assert result["status"] == "REAL_MOUNTAIN_WAVE_FROUDE_NUMBER"


def test_froude_number_is_never_negative_for_real_non_negative_wind():
    for wind in (0.0, 5.0, 15.0, 40.0):
        result = compute_real_mountain_wave_froude_number_at_point(
            wind_speed_perpendicular=wind, brunt_vaisala_n=0.015, mountain_height_m=1200.0
        )
        assert result["froude_number"] >= 0.0
        assert not math.isnan(result["froude_number"])


# --------------------------------- validate_physics (§11, opt-in PhysicsGuard)


def test_validate_physics_defaults_to_false_and_never_raises_for_out_of_range_input():
    result = compute_real_mountain_wave_froude_number_at_point(
        wind_speed_perpendicular=200.0, brunt_vaisala_n=0.02, mountain_height_m=1500.0
    )
    assert result["is_real_data"] is True


def test_validate_physics_true_passes_silently_for_real_valid_inputs():
    result = compute_real_mountain_wave_froude_number_at_point(
        wind_speed_perpendicular=15.0, brunt_vaisala_n=0.02, mountain_height_m=1500.0, validate_physics=True
    )
    assert result["is_real_data"] is True


def test_validate_physics_true_raises_for_out_of_range_wind_speed():
    with pytest.raises(RangeError):
        compute_real_mountain_wave_froude_number_at_point(
            wind_speed_perpendicular=200.0, brunt_vaisala_n=0.02, mountain_height_m=1500.0, validate_physics=True
        )
