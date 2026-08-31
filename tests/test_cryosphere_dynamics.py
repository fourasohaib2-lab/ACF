from acf.model4d.physics.cryosphere_dynamics import CryosphereDynamicsPhysics


def test_snow_melt_rate():
    assert CryosphereDynamicsPhysics.snow_melt_rate(334000, 334000) == 1


def test_ice_volume():
    assert CryosphereDynamicsPhysics.ice_volume(10, 100) == 1000


def test_glacier_mass():
    assert CryosphereDynamicsPhysics.glacier_mass(1000) == 900000


def test_albedo_effect():
    assert CryosphereDynamicsPhysics.albedo_effect(1000, 0.8) == 200


def test_freezing_rate():
    assert CryosphereDynamicsPhysics.freezing_rate(10, 2) == 20


def test_permafrost_stability():
    assert CryosphereDynamicsPhysics.permafrost_stability(100, 30) == 70


def test_glacier_retreat():
    assert CryosphereDynamicsPhysics.glacier_retreat(500, 50) == 450


def test_ice_energy():
    assert CryosphereDynamicsPhysics.ice_energy(2, 334000) == 668000


def test_snow_water_equivalent():
    assert CryosphereDynamicsPhysics.snow_water_equivalent(100, 0.3) == 30


def test_energy_balance():
    assert CryosphereDynamicsPhysics.cryosphere_energy_balance(500, 200) == 300
