from acf.model4d.physics.surface_layer_physics import SurfaceLayerPhysics


def test_wind_profile():
    value = SurfaceLayerPhysics.wind_profile(
        20,
        10
    )
    assert value == 20


def test_roughness_length():
    value = SurfaceLayerPhysics.roughness_length(
        "ocean"
    )
    assert value == 0.0002


def test_friction_velocity():
    value = SurfaceLayerPhysics.friction_velocity(
        100
    )
    assert value == 10


def test_surface_flux():
    value = SurfaceLayerPhysics.surface_flux(
        2,
        5,
        10
    )
    assert value == 100


def test_heat_flux():
    value = SurfaceLayerPhysics.heat_flux(
        10,
        5
    )
    assert value == 50


def test_momentum_flux():
    value = SurfaceLayerPhysics.momentum_flux(
        10
    )
    assert value == 100


def test_turbulence_intensity():
    value = SurfaceLayerPhysics.turbulence_intensity(
        20,
        10
    )
    assert value == 2


def test_monin_obukhov_length():
    value = SurfaceLayerPhysics.monin_obukhov_length(
        100,
        9
    )
    assert value == 10


def test_surface_temperature_gradient():
    value = SurfaceLayerPhysics.surface_temperature_gradient(
        300,
        290
    )
    assert value == 10


def test_exchange_coefficient():
    value = SurfaceLayerPhysics.exchange_coefficient(
        100,
        4
    )
    assert value == 20
