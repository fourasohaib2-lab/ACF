from acf.model4d.physics.hydrology_atmosphere_interaction import (
    HydrologyAtmosphereInteractionPhysics
)


def test_infiltration_rate():
    assert HydrologyAtmosphereInteractionPhysics.infiltration_rate(
        100,
        30
    ) == 70


def test_runoff_generation():
    assert HydrologyAtmosphereInteractionPhysics.runoff_generation(
        100,
        60
    ) == 40


def test_soil_water_storage():
    assert HydrologyAtmosphereInteractionPhysics.soil_water_storage(
        200,
        50
    ) == 250


def test_evaporation_flux():
    assert HydrologyAtmosphereInteractionPhysics.evaporation_flux(
        300,
        3
    ) == 100


def test_evapotranspiration_rate():
    assert HydrologyAtmosphereInteractionPhysics.evapotranspiration_rate(
        40,
        20
    ) == 60


def test_soil_moisture_change():
    assert HydrologyAtmosphereInteractionPhysics.soil_moisture_change(
        90,
        30
    ) == 60


def test_groundwater_recharge():
    assert HydrologyAtmosphereInteractionPhysics.groundwater_recharge(
        80,
        20
    ) == 60


def test_hydrological_balance():
    assert HydrologyAtmosphereInteractionPhysics.hydrological_balance(
        200,
        80
    ) == 120


def test_atmospheric_humidity_feedback():
    assert HydrologyAtmosphereInteractionPhysics.atmospheric_humidity_feedback(
        70,
        30
    ) == 40


def test_water_cycle_intensity():
    assert HydrologyAtmosphereInteractionPhysics.water_cycle_intensity(
        50,
        20
    ) == 1000

