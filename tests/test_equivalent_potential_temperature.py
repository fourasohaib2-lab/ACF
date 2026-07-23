import pytest

from acf.science.equivalent_potential_temperature import (
    EquivalentPotentialTemperature,
)


def test_thetae():
    thetae = EquivalentPotentialTemperature.calculate(
        300.0,
        0.010,
    )

    assert thetae > 300.0


def test_zero_humidity():
    thetae = EquivalentPotentialTemperature.calculate(
        300.0,
        0.0,
    )

    assert thetae == 300.0


def test_invalid_temperature():
    with pytest.raises(ValueError):
        EquivalentPotentialTemperature.calculate(
            0.0,
            0.01,
        )


def test_invalid_humidity():
    with pytest.raises(ValueError):
        EquivalentPotentialTemperature.calculate(
            300.0,
            -0.1,
        )
