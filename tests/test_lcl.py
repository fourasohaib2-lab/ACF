import pytest

from acf.science.lcl import LCL


def test_lcl():
    h = LCL.calculate(
        30.0,
        20.0,
    )

    assert h == 1250.0


def test_saturated():
    assert LCL.calculate(
        20.0,
        20.0,
    ) == 0.0


def test_invalid():
    with pytest.raises(ValueError):
        LCL.calculate(
            20.0,
            25.0,
        )

