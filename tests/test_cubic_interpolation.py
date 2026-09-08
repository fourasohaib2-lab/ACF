"""
Tests for CubicInterpolation
"""

from acf.model4d.interpolation.cubic import CubicInterpolation


def test_left_endpoint():
    assert CubicInterpolation.interpolate(0, 10, 20, 30, 0.0) == 10


def test_right_endpoint():
    assert CubicInterpolation.interpolate(0, 10, 20, 30, 1.0) == 20


def test_middle_value():
    value = CubicInterpolation.interpolate(0, 10, 20, 30, 0.5)
    assert 10 < value < 20


def test_constant_field():
    value = CubicInterpolation.interpolate(5, 5, 5, 5, 0.4)
    assert value == 5


def test_increasing_field():
    value = CubicInterpolation.interpolate(1, 2, 3, 4, 0.25)
    assert 2 < value < 3


def test_decreasing_field():
    value = CubicInterpolation.interpolate(4, 3, 2, 1, 0.75)
    assert 2 < value < 3
