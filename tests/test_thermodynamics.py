from acf.model4d.physics.thermodynamics import Thermodynamics


def test_temperature_conversion():
    assert Thermodynamics.temperature_conversion(0) == 273.15


def test_temperature_conversion_positive():
    assert Thermodynamics.temperature_conversion(20) == 293.15


def test_density():
    rho = Thermodynamics.pressure_density(
        pressure=101325,
        temperature=288.15
    )

    assert round(rho, 3) == 1.225


def test_density_low_pressure():
    rho = Thermodynamics.pressure_density(
        pressure=80000,
        temperature=280
    )

    assert rho > 0


def test_potential_temperature():
    theta = Thermodynamics.potential_temperature(
        temperature=280,
        pressure=100000
    )

    assert theta == 280


def test_potential_temperature_lower_pressure():
    theta = Thermodynamics.potential_temperature(
        temperature=280,
        pressure=90000
    )

    assert theta > 280


def test_heat_index_cold():
    assert Thermodynamics.heat_index(240) == "Cold"


def test_heat_index_normal():
    assert Thermodynamics.heat_index(270) == "Normal"


def test_heat_index_warm():
    assert Thermodynamics.heat_index(300) == "Warm"


def test_heat_index_hot():
    assert Thermodynamics.heat_index(320) == "Hot"
