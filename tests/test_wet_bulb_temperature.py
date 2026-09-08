import pytest

from acf.science.wet_bulb_temperature import WetBulbTemperature


def test_wet_bulb():
    tw = WetBulbTemperature.calculate(30.0, 0.70)

    assert 24.0 < tw < 27.0


def test_hundred_percent():
    tw = WetBulbTemperature.calculate(20.0, 1.0)

    assert abs(tw - 20.0) < 1.0


def test_invalid():
    with pytest.raises(ValueError):
        WetBulbTemperature.calculate(20.0, 1.5)
