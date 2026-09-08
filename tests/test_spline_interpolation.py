from acf.model4d.interpolation.spline import SplineInterpolation


def test_left_endpoint():
    assert SplineInterpolation.endpoints(10, 20)[0] == 10


def test_right_endpoint():
    assert SplineInterpolation.endpoints(10, 20)[1] == 20


def test_midpoint():
    value = SplineInterpolation.midpoint(0, 10, 20, 30)
    assert 10 < value < 20


def test_constant():
    value = SplineInterpolation.interpolate(5, 5, 5, 5, 0.4)
    assert value == 5


def test_interpolation():
    value = SplineInterpolation.interpolate(1, 2, 3, 4, 0.5)
    assert 2 < value < 3


def test_reverse():
    value = SplineInterpolation.interpolate(4, 3, 2, 1, 0.5)
    assert 2 < value < 3


def test_zero():
    assert SplineInterpolation.interpolate(0, 0, 0, 0, 0.5) == 0


def test_midpoint_constant():
    assert SplineInterpolation.midpoint(2, 2, 2, 2) == 2
