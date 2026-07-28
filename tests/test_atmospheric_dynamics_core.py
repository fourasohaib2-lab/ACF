from acf.model4d.physics.atmospheric_dynamics_core import (
    AtmosphericDynamicsCore,
    AtmosphericDynamicsState,
)


def create_state():

    return AtmosphericDynamicsState(
        temperature=300,
        humidity=12,
        pressure=100000,
        wind_speed=10,
        vertical_velocity=3,
        radiation_flux=250,
        convection=5,
        precipitation=4,
        surface_energy=320,
    )


def test_temperature_dynamics():

    model = AtmosphericDynamicsCore()

    assert model.temperature_dynamics(create_state()) == 301.5


def test_humidity_transport():

    model = AtmosphericDynamicsCore()

    assert model.humidity_transport(create_state()) == 8.5


def test_pressure_dynamics():

    model = AtmosphericDynamicsCore()

    assert model.pressure_dynamics(create_state()) == 1012.5


def test_wind_circulation():

    model = AtmosphericDynamicsCore()

    assert model.wind_circulation(create_state()) == 12.0


def test_vertical_convection():

    model = AtmosphericDynamicsCore()

    assert model.vertical_convection(create_state()) == 6.5


def test_energy_transport():

    model = AtmosphericDynamicsCore()

    assert model.energy_transport(create_state()) == 45.0


def test_mass_transport():

    model = AtmosphericDynamicsCore()

    assert model.mass_transport(create_state()) == 25.0


def test_dynamic_stability_index():

    model = AtmosphericDynamicsCore()

    assert model.dynamic_stability_index(create_state()) == 9.5
