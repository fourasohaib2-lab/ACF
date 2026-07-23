import pytest

from acf.science.virtual_potential_temperature import (
    VirtualPotentialTemperature,
)


def test_theta_v():
    theta = VirtualPotentialTemperature.calculate(
        300.0,
        0.010,
    )

    assert theta > 300.0


def test_zero():
    theta = VirtualPotentialTemperature.calculate(
        300.0,
        0.0,
    )

    assert theta == 300.0


def test_invalid_temperature():
    with pytest.raises(ValueError):
        VirtualPotentialTemperature.calculate(
            0.0,
            0.01,
        )


def test_invalid_ratio():
    with pytest.raises(ValueError):
        VirtualPotentialTemperature.calculate(
            300.0,
            -1.0,
        )
