from acf.model4d.physics.soil_atmosphere_interaction import SoilAtmosphereInteractionPhysics


def test_evaporation_rate():
    value = SoilAtmosphereInteractionPhysics.evaporation_rate(
        100,
        20
    )
    assert value == 2000


def test_soil_heat_flux():
    value = SoilAtmosphereInteractionPhysics.soil_heat_flux(
        50,
        2
    )
    assert value == 100


def test_surface_temperature_effect():
    value = SoilAtmosphereInteractionPhysics.surface_temperature_effect(
        300,
        280
    )
    assert value == 20


def test_soil_moisture_loss():
    value = SoilAtmosphereInteractionPhysics.soil_moisture_loss(
        80,
        30
    )
    assert value == 50


def test_latent_heat_flux():
    value = SoilAtmosphereInteractionPhysics.latent_heat_flux(
        200,
        2
    )
    assert value == 400


def test_albedo_effect():
    value = SoilAtmosphereInteractionPhysics.albedo_effect(
        100,
        0.3
    )
    assert value == 30


def test_ground_flux():
    value = SoilAtmosphereInteractionPhysics.ground_flux(
        500,
        200
    )
    assert value == 300


def test_evapotranspiration():
    value = SoilAtmosphereInteractionPhysics.evapotranspiration(
        100,
        40
    )
    assert value == 60


def test_soil_temperature_change():
    value = SoilAtmosphereInteractionPhysics.soil_temperature_change(
        25,
        5
    )
    assert value == 30


def test_surface_energy_balance():
    value = SoilAtmosphereInteractionPhysics.surface_energy_balance(
        400,
        150
    )
    assert value == 250
