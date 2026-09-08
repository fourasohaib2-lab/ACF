from acf.model4d.physics.magnetosphere_dynamics import MagnetosphereDynamicsPhysics


def test_solar_wind_pressure():
    assert MagnetosphereDynamicsPhysics.solar_wind_pressure(2, 10) == 200


def test_magnetic_pressure():
    assert MagnetosphereDynamicsPhysics.magnetic_pressure(10) == 50


def test_magnetopause_distance():
    value = MagnetosphereDynamicsPhysics.magnetopause_distance(4)

    assert value == 50


def test_geomagnetic_activity():
    assert MagnetosphereDynamicsPhysics.geomagnetic_activity(10) == "quiet"


def test_geomagnetic_storm():
    assert MagnetosphereDynamicsPhysics.geomagnetic_activity(90) == "extreme"


def test_particle_trapping():
    assert MagnetosphereDynamicsPhysics.particle_trapping(0.5, 100) == 50


def test_aurora_intensity():
    assert MagnetosphereDynamicsPhysics.aurora_intensity(10, 5) == 50


def test_radiation_belt_energy():
    assert MagnetosphereDynamicsPhysics.radiation_belt_energy(10, 20) == 200


def test_magnetic_reconnection():
    assert MagnetosphereDynamicsPhysics.magnetic_reconnection(5, 10) == 50


def test_storm_energy():
    assert MagnetosphereDynamicsPhysics.storm_energy(20, 5) == 100
