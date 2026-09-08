from acf.model4d.physics.snow_ice_atmosphere_interaction import SnowIceAtmosphereInteractionPhysics


def test_snow_accumulation():
    assert SnowIceAtmosphereInteractionPhysics.snow_accumulation(100, 0.5) == 50


def test_snow_melt_energy():
    assert SnowIceAtmosphereInteractionPhysics.snow_melt_energy(10) == 3340


def test_snow_water_equivalent():
    assert SnowIceAtmosphereInteractionPhysics.snow_water_equivalent(100) == 10


def test_ice_albedo_effect():
    assert SnowIceAtmosphereInteractionPhysics.ice_albedo_effect(1000, 0.8) == 800


def test_absorbed_solar_energy():
    assert SnowIceAtmosphereInteractionPhysics.absorbed_solar_energy(1000, 0.8) == 200


def test_freezing_potential():
    assert SnowIceAtmosphereInteractionPhysics.freezing_potential(260) == 13


def test_surface_cooling():
    assert SnowIceAtmosphereInteractionPhysics.surface_cooling(280, 260) == 20


def test_ice_insulation():
    value = SnowIceAtmosphereInteractionPhysics.ice_insulation(2)
    assert round(value, 3) == 0.909


def test_freeze_thaw_cycle():
    assert SnowIceAtmosphereInteractionPhysics.freeze_thaw_cycle(5, 3) == 8


def test_snow_cover_effect():
    assert SnowIceAtmosphereInteractionPhysics.snow_cover_effect(1000, 0.6) == 600
