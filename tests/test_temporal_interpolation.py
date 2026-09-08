"""
Atmospheric Complexity Framework (ACF)

MODEL4D - Temporal Interpolation Test Suite

This file was previously empty - pytest collected it but ran no tests,
so the real source module (src/acf/model4d/interpolation/temporal.py)
had 0% coverage and was never actually verified. Added real tests
exercising the actual source class.
"""

import numpy as np
import pytest

from acf.model4d.interpolation.temporal import TemporalInterpolation


def test_fraction():
    assert TemporalInterpolation.fraction(0.0, 10.0, 5.0) == pytest.approx(0.5)


def test_fraction_rejects_equal_times():
    with pytest.raises(ValueError):
        TemporalInterpolation.fraction(5.0, 5.0, 5.0)


def test_interpolate_scalar():
    result = TemporalInterpolation.interpolate(0.0, 10.0, 10.0, 20.0, 5.0)
    assert result == pytest.approx(15.0)


def test_interpolate_array():
    v0 = np.array([0.0, 10.0])
    v1 = np.array([10.0, 20.0])
    result = TemporalInterpolation.interpolate(0.0, v0, 10.0, v1, 5.0)
    np.testing.assert_allclose(result, np.array([5.0, 15.0]))


def test_nearest():
    times = [0.0, 6.0, 12.0, 18.0]
    values = [1.0, 2.0, 3.0, 4.0]
    assert TemporalInterpolation.nearest(times, values, 7.0) == 2.0
    assert TemporalInterpolation.nearest(times, values, 17.0) == 4.0


def test_nearest_rejects_empty_series():
    with pytest.raises(ValueError):
        TemporalInterpolation.nearest([], [], 1.0)


def test_interpolate_series_linear_between_points():
    times = [0.0, 6.0, 12.0]
    values = [280.0, 285.0, 290.0]
    result = TemporalInterpolation.interpolate_series(times, values, 9.0)
    assert result == pytest.approx(287.5)


def test_interpolate_series_clamps_outside_range():
    times = [0.0, 6.0, 12.0]
    values = [280.0, 285.0, 290.0]
    assert TemporalInterpolation.interpolate_series(times, values, -5.0) == pytest.approx(280.0)
    assert TemporalInterpolation.interpolate_series(times, values, 100.0) == pytest.approx(290.0)


def test_interpolate_series_nearest_method():
    times = [0.0, 6.0, 12.0]
    values = [280.0, 285.0, 290.0]
    result = TemporalInterpolation.interpolate_series(times, values, 7.0, method="nearest")
    assert result == 285.0


def test_interpolate_series_rejects_too_few_points():
    with pytest.raises(ValueError):
        TemporalInterpolation.interpolate_series([0.0], [1.0], 0.0)


def test_interpolate_series_rejects_mismatched_lengths():
    with pytest.raises(ValueError):
        TemporalInterpolation.interpolate_series([0.0, 1.0], [1.0], 0.5)
