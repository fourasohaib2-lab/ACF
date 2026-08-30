import pytest

from acf.science.lcl import LCL


def test_lcl():
    h = LCL.calculate(
        30.0,
        20.0,
    )

    assert h == 1250.0


def test_saturated():
    assert (
        LCL.calculate(
            20.0,
            20.0,
        )
        == 0.0
    )


def test_invalid():
    with pytest.raises(ValueError):
        LCL.calculate(
            20.0,
            25.0,
        )


def test_bolton_close_to_espy_approximation():
    # For a typical 10 degC dewpoint depression, Bolton's physically
    # grounded height should be in the same ballpark as Espy's fixed
    # ~125 m/degC rule (within roughly 5%), not wildly different.
    espy = LCL.calculate(30.0, 20.0)
    bolton = LCL.calculate_bolton_celsius(30.0, 20.0)
    assert bolton == pytest.approx(espy, rel=0.05)


def test_bolton_saturated_air_gives_zero_height():
    h = LCL.calculate_bolton_celsius(20.0, 20.0)
    assert h == pytest.approx(0.0, abs=1e-6)


def test_bolton_kelvin_and_celsius_wrappers_agree():
    assert LCL.calculate_bolton(303.15, 293.15) == pytest.approx(LCL.calculate_bolton_celsius(30.0, 20.0))


def test_bolton_invalid_dewpoint_exceeds_temperature():
    with pytest.raises(ValueError):
        LCL.calculate_bolton_celsius(20.0, 25.0)
