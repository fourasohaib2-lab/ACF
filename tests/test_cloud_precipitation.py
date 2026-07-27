from acf.model4d.physics.cloud_precipitation import CloudPrecipitationPhysics


def test_precipitation_rate():
    assert CloudPrecipitationPhysics.precipitation_rate(
        10,
        2
    ) == 5


def test_rainfall_volume():
    assert CloudPrecipitationPhysics.rainfall_volume(
        100,
        2
    ) == 200


def test_terminal_velocity():
    value = CloudPrecipitationPhysics.terminal_velocity(
        100,
        2
    )
    assert value == 0.002


def test_drop_mass():
    value = CloudPrecipitationPhysics.rain_drop_mass(
        1
    )
    assert round(value, 6) == 0.000004


def test_collision():
    assert CloudPrecipitationPhysics.collision_coalescence(
        10,
        0.5
    ) == 5


def test_evaporation():
    assert CloudPrecipitationPhysics.evaporation_rate(
        100,
        0.2
    ) == 80


def test_snowfall():
    assert CloudPrecipitationPhysics.snowfall_rate(
        10,
        5
    ) == 50


def test_flux():
    assert CloudPrecipitationPhysics.precipitation_flux(
        2,
        10
    ) == 20


def test_latent_heat():
    assert CloudPrecipitationPhysics.latent_heat_release(
        2,
        100
    ) == 200


def test_efficiency():
    assert CloudPrecipitationPhysics.precipitation_efficiency(
        50,
        100
    ) == 0.5
