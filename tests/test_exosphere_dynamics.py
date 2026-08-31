from acf.model4d.physics.exosphere_dynamics import ExosphereDynamicsPhysics


def test_exosphere_density():
    assert ExosphereDynamicsPhysics.exosphere_density(100, 0.5) == 50


def test_atmospheric_escape_rate():
    assert ExosphereDynamicsPhysics.atmospheric_escape_rate(1000, 0.1) == 100


def test_solar_wind_interaction():
    assert ExosphereDynamicsPhysics.solar_wind_interaction(100, 0.8) == 19.999999999999996


def test_exosphere_temperature():
    assert ExosphereDynamicsPhysics.exosphere_temperature(500, 50) == 550


def test_thermal_escape_velocity():
    assert ExosphereDynamicsPhysics.thermal_escape_velocity(20, 2) == 40


def test_atmospheric_loss():
    assert ExosphereDynamicsPhysics.atmospheric_loss(1000, 200) == 800


def test_particle_escape_fraction():
    assert ExosphereDynamicsPhysics.particle_escape_fraction(1000, 100) == 0.1


def test_energy_balance():
    assert ExosphereDynamicsPhysics.exosphere_energy_balance(500, 200) == 300


def test_solar_activity_effect():
    assert ExosphereDynamicsPhysics.solar_activity_effect(50, 2) == 100


def test_upper_atmosphere_expansion():
    assert ExosphereDynamicsPhysics.upper_atmosphere_expansion(300, 1.5) == 450
