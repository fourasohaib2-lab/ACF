from acf.model4d.physics.solar_wind_interaction import (
    SolarWindInteractionPhysics
)


def test_solar_wind_pressure():
    value = SolarWindInteractionPhysics.solar_wind_pressure(
        2,
        10
    )
    assert value == 100


def test_solar_wind_energy_flux():
    value = SolarWindInteractionPhysics.solar_wind_energy_flux(
        2,
        10
    )
    assert value == 1000


def test_magnetopause_distance():
    value = SolarWindInteractionPhysics.magnetopause_distance(
        4,
        16
    )
    assert value == 2


def test_speed_change():
    value = SolarWindInteractionPhysics.solar_wind_speed_change(
        400,
        500
    )
    assert value == 100


def test_density_variation():
    value = SolarWindInteractionPhysics.plasma_density_variation(
        5,
        8
    )
    assert value == 3


def test_magnetic_effect():
    value = SolarWindInteractionPhysics.magnetic_field_effect(
        20,
        10
    )
    assert value == 2


def test_geomagnetic_activity():
    value = SolarWindInteractionPhysics.geomagnetic_activity_index(
        5,
        4
    )
    assert value == 20


def test_solar_storm():
    value = SolarWindInteractionPhysics.solar_storm_intensity(
        3,
        100
    )
    assert value == 300


def test_aurora_probability():
    value = SolarWindInteractionPhysics.aurora_probability(
        0.5,
        0.5
    )
    assert value == 0.25


def test_interaction_strength():
    value = SolarWindInteractionPhysics.interaction_strength(
        10,
        5
    )
    assert value == 50
