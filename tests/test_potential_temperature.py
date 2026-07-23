from acf.science.potential_temperature import PotentialTemperature


def test_potential_temperature():

    theta = PotentialTemperature.calculate(
        temperature_k=300.0,
        pressure_hpa=1000.0,
    )

    assert round(theta, 2) == 300.00


def test_potential_temperature_lower_pressure():

    theta = PotentialTemperature.calculate(
        temperature_k=300.0,
        pressure_hpa=850.0,
    )

    assert theta > 300.0
