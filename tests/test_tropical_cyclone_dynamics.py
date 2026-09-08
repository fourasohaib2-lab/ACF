from acf.model4d.physics.tropical_cyclone_dynamics import TropicalCycloneDynamicsPhysics


def test_pressure_gradient_force():
    value = TropicalCycloneDynamicsPhysics.pressure_gradient_force(100, 10)
    assert value == 10


def test_cyclone_intensity():
    value = TropicalCycloneDynamicsPhysics.cyclone_intensity(50, 25)
    assert value == 100


def test_coriolis_effect():
    value = TropicalCycloneDynamicsPhysics.coriolis_effect(30, 10)
    assert round(value, 6) == 0.000729


def test_gradient_balance():
    value = TropicalCycloneDynamicsPhysics.gradient_wind_balance(20, 5)
    assert value == 25


def test_cyclone_energy():
    value = TropicalCycloneDynamicsPhysics.cyclone_energy(100, 10)
    assert value == 5000


def test_eyewall_radius():
    value = TropicalCycloneDynamicsPhysics.eyewall_radius_change(100, 20)
    assert value == 80


def test_moisture_energy():
    value = TropicalCycloneDynamicsPhysics.moisture_energy(10, 2500)
    assert value == 25000


def test_lifetime():
    value = TropicalCycloneDynamicsPhysics.cyclone_lifetime(1000, 100)
    assert value == 10


def test_rapid_intensification():
    value = TropicalCycloneDynamicsPhysics.rapid_intensification(40, 70)
    assert value == 30


def test_storm_surge():
    value = TropicalCycloneDynamicsPhysics.storm_surge_height(10, 0.5)
    assert value == 50
