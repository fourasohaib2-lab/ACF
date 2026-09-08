from acf.model4d.physics.mesospheric_dynamics import MesosphericDynamicsPhysics


def test_temperature_gradient():
    assert MesosphericDynamicsPhysics.temperature_gradient(250, 150) == 100


def test_radiative_cooling():
    assert MesosphericDynamicsPhysics.radiative_cooling(100, 0.5) == 50


def test_mesospheric_pressure():
    assert MesosphericDynamicsPhysics.mesospheric_pressure(1000, 10) == 100


def test_atmospheric_density():
    assert MesosphericDynamicsPhysics.atmospheric_density(200, 100) == 2


def test_wind_velocity():
    assert MesosphericDynamicsPhysics.wind_velocity(50, 5) == 10


def test_energy_transfer():
    assert MesosphericDynamicsPhysics.energy_transfer(300, 200) == 500


def test_gravity_wave_effect():
    assert MesosphericDynamicsPhysics.gravity_wave_effect(10, 2) == 20


def test_molecular_diffusion():
    assert MesosphericDynamicsPhysics.molecular_diffusion(5, 10) == 50


def test_ozone_interaction():
    assert MesosphericDynamicsPhysics.ozone_interaction(20, 3) == 60


def test_mesospheric_energy_balance():
    assert MesosphericDynamicsPhysics.mesospheric_energy_balance(500, 200) == 300
