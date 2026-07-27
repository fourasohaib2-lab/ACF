from acf.model4d.physics.thermospheric_dynamics import (
    ThermosphericDynamicsPhysics
)


def test_solar_heating_flux():
    assert ThermosphericDynamicsPhysics.solar_heating_flux(
        1000, 0.5
    ) == 500


def test_thermospheric_temperature():
    assert ThermosphericDynamicsPhysics.thermospheric_temperature(
        500, 50
    ) == 550


def test_atmospheric_density():
    assert ThermosphericDynamicsPhysics.atmospheric_density(
        100, 20
    ) == 5


def test_thermal_expansion():
    assert ThermosphericDynamicsPhysics.thermal_expansion(
        0.02, 100
    ) == 2


def test_radiative_cooling():
    assert ThermosphericDynamicsPhysics.radiative_cooling(
        1000, 0.1
    ) == 100


def test_ionosphere_temperature_effect():
    assert ThermosphericDynamicsPhysics.ionosphere_temperature_effect(
        50, 2
    ) == 100


def test_thermosphere_pressure():
    assert ThermosphericDynamicsPhysics.thermosphere_pressure(
        5, 200
    ) == 1000


def test_molecular_diffusion():
    assert ThermosphericDynamicsPhysics.molecular_diffusion(
        10, 5
    ) == 50


def test_atmospheric_escape_velocity():
    assert ThermosphericDynamicsPhysics.atmospheric_escape_velocity(
        300, 2
    ) == 600


def test_energy_balance():
    assert ThermosphericDynamicsPhysics.energy_balance(
        1000, 300
    ) == 700
