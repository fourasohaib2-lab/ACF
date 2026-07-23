from acf.science.hypsometric_equation import (
    HypsometricEquation,
)

import pytest


def test_hypsometric():
    dz = HypsometricEquation.calculate(
        pressure1_pa=100000.0,
        pressure2_pa=90000.0,
        virtual_temperature_k=280.0,
    )

    assert dz > 800


def test_invalid_pressure():
    with pytest.raises(ValueError):
        HypsometricEquation.calculate(
            0.0,
            90000.0,
            280.0,
        )


def test_invalid_temperature():
    with pytest.raises(ValueError):
        HypsometricEquation.calculate(
            100000.0,
            90000.0,
            0.0,
        )
