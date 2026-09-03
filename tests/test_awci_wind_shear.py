"""
Tests for acf.awci.wind_shear - real per-point bulk wind shear (docs/
ACF_MASTER_PROMPT.md section 12, explicit user request "commence par
le module dynamique, avec le cisaillement de vent"). This session's
exhaustive 90-section conformance audit (reports/ACF_MASTER_AUDIT_v2.md)
found this real, already-existing formula
(acf.science.bulk_wind_shear.BulkWindShear) was never wired into
anything that computes ACF's real outputs.
"""

from __future__ import annotations

import math
import random

import pytest

from acf.awci.wind_shear import compute_real_wind_shear_at_point
from acf.core.exceptions import RangeError
from acf.science.bulk_wind_shear import BulkWindShear


def test_matches_a_direct_bulkwindshear_call():
    u_profile = [5.0, 8.0, 12.0, 20.0]
    v_profile = [0.0, 2.0, 4.0, 10.0]

    result = compute_real_wind_shear_at_point(u_profile, v_profile)

    expected = BulkWindShear.calculate(u_profile[0], v_profile[0], u_profile[-1], v_profile[-1])
    assert result["shear_m_s"] == pytest.approx(expected)


def test_zero_shear_when_top_and_bottom_wind_are_identical():
    u_profile = [10.0, 10.0, 10.0]
    v_profile = [5.0, 5.0, 5.0]
    result = compute_real_wind_shear_at_point(u_profile, v_profile)
    assert result["shear_m_s"] == pytest.approx(0.0)


def test_real_pythagorean_shear_matches_a_hand_computed_value():
    """u changes by 3, v changes by 4 -> real shear = 5 (3-4-5 triangle) - independently verifiable by hand."""
    u_profile = [0.0, 3.0]
    v_profile = [0.0, 4.0]
    result = compute_real_wind_shear_at_point(u_profile, v_profile)
    assert result["shear_m_s"] == pytest.approx(5.0)


def test_default_levels_span_the_full_profile():
    u_profile = [1.0, 2.0, 3.0, 4.0, 5.0]
    v_profile = [0.0, 0.0, 0.0, 0.0, 0.0]
    result = compute_real_wind_shear_at_point(u_profile, v_profile)
    assert result["bottom_level"] == 0
    assert result["top_level"] == 4  # real resolved index for -1 on a 5-level profile


def test_custom_levels_are_used_and_resolved():
    u_profile = [1.0, 2.0, 3.0, 4.0]
    v_profile = [0.0, 0.0, 0.0, 0.0]
    result = compute_real_wind_shear_at_point(u_profile, v_profile, bottom_level=1, top_level=2)
    assert result["bottom_level"] == 1
    assert result["top_level"] == 2
    assert result["shear_m_s"] == pytest.approx(1.0)


def test_out_of_range_level_raises():
    u_profile = [1.0, 2.0]
    v_profile = [0.0, 0.0]
    with pytest.raises(IndexError):
        compute_real_wind_shear_at_point(u_profile, v_profile, top_level=5)


def test_is_real_data_and_status_are_honest():
    result = compute_real_wind_shear_at_point([1.0, 2.0], [0.0, 0.0])
    assert result["is_real_data"] is True
    assert result["status"] == "REAL_BULK_WIND_SHEAR"


def test_shear_is_never_negative():
    """A real vector-magnitude shear can never be negative - real physical invariant, not just a code assertion."""
    for _ in range(5):
        u = [random.uniform(-50, 50) for _ in range(4)]
        v = [random.uniform(-50, 50) for _ in range(4)]
        result = compute_real_wind_shear_at_point(u, v)
        assert result["shear_m_s"] >= 0.0
        assert not math.isnan(result["shear_m_s"])


# --------------------------------- validate_physics (§11, opt-in PhysicsGuard)


def test_validate_physics_defaults_to_false_and_never_raises_for_out_of_range_input():
    result = compute_real_wind_shear_at_point([1.0, 200.0], [0.0, 0.0])
    assert result["is_real_data"] is True


def test_validate_physics_true_passes_silently_for_real_valid_inputs():
    result = compute_real_wind_shear_at_point([5.0, 12.0], [0.0, 4.0], validate_physics=True)
    assert result["is_real_data"] is True


def test_validate_physics_true_raises_for_out_of_range_u_component():
    with pytest.raises(RangeError):
        compute_real_wind_shear_at_point([1.0, 200.0], [0.0, 0.0], validate_physics=True)


def test_validate_physics_true_raises_for_out_of_range_v_component():
    with pytest.raises(RangeError):
        compute_real_wind_shear_at_point([1.0, 5.0], [0.0, -200.0], validate_physics=True)
