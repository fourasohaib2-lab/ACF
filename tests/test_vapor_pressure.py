import pytest

from acf.science.vapor_pressure import VaporPressure


def test_vapor_pressure():
    # q = 0.01, p = 1000 hPa
    e = VaporPressure.calculate(0.01, 1000.0)
    # Expected: 0.01 * 1000 / (0.622 + 0.01 * 0.378) ≈ 15.98 hPa
    assert round(e, 2) == 15.98


def test_zero_humidity():
    assert VaporPressure.calculate(0.0, 1000.0) == 0.0


def test_invalid_humidity():
    with pytest.raises(ValueError):
        VaporPressure.calculate(1.5, 1000.0)
