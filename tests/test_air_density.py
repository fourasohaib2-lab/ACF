import pytest

from acf.science.air_density import AirDensity


def test_air_density():
    rho = AirDensity.calculate(
        pressure_pa=101325.0,
        temperature_k=288.15,
    )

    assert round(rho, 3) == 1.225


def test_invalid_pressure():
    with pytest.raises(ValueError):
        AirDensity.calculate(
            pressure_pa=0.0,
            temperature_k=288.15,
        )


def test_invalid_temperature():
    with pytest.raises(ValueError):
        AirDensity.calculate(
            pressure_pa=101325.0,
            temperature_k=0.0,
        )
