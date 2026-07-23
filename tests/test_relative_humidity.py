from acf.science.relative_humidity import RelativeHumidity

import pytest


def test_relative_humidity():
    rh = RelativeHumidity.calculate(
        vapor_pressure=10.0,
        saturation_vapor_pressure=20.0,
    )

    assert rh == 0.5


def test_zero():
    assert (
        RelativeHumidity.calculate(0.0, 20.0)
        == 0.0
    )


def test_full():
    assert (
        RelativeHumidity.calculate(20.0, 20.0)
        == 1.0
    )


def test_invalid():
    with pytest.raises(ValueError):
        RelativeHumidity.calculate(10.0, 0.0)

