"""
Atmospheric Complexity Framework (ACF)

MODEL4D - Vertical Interpolation Test Suite

This file was previously empty - pytest collected it but ran no tests,
so the real source module (src/acf/model4d/interpolation/vertical.py)
had 0% coverage and was never actually verified. Added real tests
exercising the actual source class.
"""

import math

import numpy as np
import pytest

from acf.model4d.interpolation.vertical import VerticalInterpolation


def test_interpolate_linear():
    result = VerticalInterpolation.interpolate_linear(z0=0.0, v0=280.0, z1=1000.0, v1=270.0, z=500.0)
    assert result == pytest.approx(275.0)


def test_interpolate_linear_rejects_equal_heights():
    with pytest.raises(ValueError):
        VerticalInterpolation.interpolate_linear(500.0, 280.0, 500.0, 270.0, 500.0)


def test_interpolate_log_pressure_matches_formula():
    p0, v0, p1, v1, p = 1000.0, 288.0, 850.0, 278.0, 925.0
    expected = v0 + (math.log(p) - math.log(p0)) * (v1 - v0) / (math.log(p1) - math.log(p0))
    result = VerticalInterpolation.interpolate_log_pressure(p0, v0, p1, v1, p)
    assert result == pytest.approx(expected)


def test_interpolate_log_pressure_rejects_non_positive():
    with pytest.raises(ValueError):
        VerticalInterpolation.interpolate_log_pressure(0.0, 280.0, 850.0, 270.0, 925.0)
    with pytest.raises(ValueError):
        VerticalInterpolation.interpolate_log_pressure(1000.0, 280.0, 1000.0, 270.0, 925.0)


def test_interpolate_profile_linear_ascending():
    levels = [0.0, 1000.0, 2000.0]
    values = [288.0, 281.0, 275.0]
    result = VerticalInterpolation.interpolate_profile(levels, values, 500.0)
    assert result == pytest.approx(284.5)


def test_interpolate_profile_handles_descending_levels():
    # Pressure levels descend with height (surface = highest pressure)
    levels = [1000.0, 850.0, 700.0]
    values = [288.0, 278.0, 268.0]
    result = VerticalInterpolation.interpolate_profile(levels, values, 925.0)
    assert result == pytest.approx(283.0)


def test_interpolate_profile_clamps_outside_range():
    levels = [1000.0, 850.0, 700.0]
    values = [288.0, 278.0, 268.0]
    assert VerticalInterpolation.interpolate_profile(levels, values, 1100.0) == pytest.approx(288.0)
    assert VerticalInterpolation.interpolate_profile(levels, values, 500.0) == pytest.approx(268.0)


def test_interpolate_profile_log_coord():
    levels = [1000.0, 500.0, 250.0]
    values = [288.0, 253.0, 223.0]
    result = VerticalInterpolation.interpolate_profile(levels, values, 700.0, log_coord=True)
    lev_arr = np.log(np.array(levels)[::-1])
    vals_arr = np.array(values)[::-1]
    target = math.log(700.0)
    idx = int(np.searchsorted(lev_arr, target))
    alpha = (target - lev_arr[idx - 1]) / (lev_arr[idx] - lev_arr[idx - 1])
    expected = vals_arr[idx - 1] + alpha * (vals_arr[idx] - vals_arr[idx - 1])
    assert result == pytest.approx(expected)


def test_interpolate_profile_rejects_too_few_levels():
    with pytest.raises(ValueError):
        VerticalInterpolation.interpolate_profile([1000.0], [288.0], 900.0)


def test_interpolate_profile_rejects_mismatched_lengths():
    with pytest.raises(ValueError):
        VerticalInterpolation.interpolate_profile([1000.0, 900.0], [288.0], 950.0)
