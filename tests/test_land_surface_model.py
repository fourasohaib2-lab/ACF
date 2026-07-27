from acf.model4d.physics.land_surface_model import LandSurfaceModelPhysics


def test_soil_temperature():
    value = LandSurfaceModelPhysics.soil_temperature(
        280,
        5
    )
    assert value == 285


def test_surface_flux():
    value = LandSurfaceModelPhysics.surface_flux(
        100,
        2
    )
    assert value == 200


def test_vegetation_effect():
    value = LandSurfaceModelPhysics.vegetation_effect(
        300,
        0.5
    )
    assert value == 150


def test_snow_cover_effect():
    value = LandSurfaceModelPhysics.snow_cover_effect(
        20,
        2
    )
    assert value == 40


def test_surface_albedo():
    value = LandSurfaceModelPhysics.surface_albedo(
        500,
        0.2
    )
    assert value == 100


def test_root_zone_moisture():
    value = LandSurfaceModelPhysics.root_zone_moisture(
        80,
        30
    )
    assert value == 50


def test_roughness_length():
    value = LandSurfaceModelPhysics.roughness_length(
        10,
        3
    )
    assert value == 30


def test_energy_balance():
    value = LandSurfaceModelPhysics.energy_balance(
        400,
        150
    )
    assert value == 250


def test_water_balance():
    value = LandSurfaceModelPhysics.water_balance(
        200,
        80
    )
    assert value == 120


def test_land_surface_response():
    value = LandSurfaceModelPhysics.land_surface_response(
        100,
        4
    )
    assert value == 400
