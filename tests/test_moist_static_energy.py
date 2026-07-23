import pytest

from acf.science.moist_static_energy import (
    MoistStaticEnergy,
)


def test_mse():
    mse = MoistStaticEnergy.calculate(
        300.0,
        1000.0,
        0.010,
    )

    assert mse > 300000.0


def test_invalid_temperature():
    with pytest.raises(ValueError):
        MoistStaticEnergy.calculate(
            0.0,
            1000.0,
            0.01,
        )


def test_invalid_height():
    with pytest.raises(ValueError):
        MoistStaticEnergy.calculate(
            300.0,
            -1.0,
            0.01,
        )


def test_invalid_humidity():
    with pytest.raises(ValueError):
        MoistStaticEnergy.calculate(
            300.0,
            1000.0,
            -0.01,
        )

