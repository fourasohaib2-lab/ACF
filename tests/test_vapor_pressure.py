from acf.science.vapor_pressure import VaporPressure

import pytest


def test_vapor_pressure():
    e = VaporPressure.calculate(
        relative_humidity=0.50,
        saturation_vapor_pressure=20.0,
    )

    assert e == 10.0


def test_zero():
    assert VaporPressure.calculate(0.0, 20.0) == 0.0


def test_full():
    assert VaporPressure.calculate(1.0, 20.0) == 20.0


def test_invalid():
    with pytest.raises(ValueError):
        VaporPressure.calculate(
            relative_humidity=1.2,
            saturation_vapor_pressure=20.0,
        )
