from acf.model4d.physics.mesoscale_environment import MesoscaleEnvironmentPhysics


def test_temperature_gradient():
    value = MesoscaleEnvironmentPhysics.temperature_gradient(300, 280)
    assert value == 20


def test_pressure_gradient():
    value = MesoscaleEnvironmentPhysics.pressure_gradient(1020, 1000)
    assert value == 20


def test_moisture_flux():
    value = MesoscaleEnvironmentPhysics.moisture_flux(5, 10)
    assert value == 50


def test_boundary_layer_height():
    value = MesoscaleEnvironmentPhysics.boundary_layer_height(100, 10)
    assert value == 10


def test_mesoscale_convection_index():
    value = MesoscaleEnvironmentPhysics.mesoscale_convection_index(200, 3)
    assert value == 600


def test_convergence():
    value = MesoscaleEnvironmentPhysics.convergence(30, 10)
    assert value == 20


def test_vertical_velocity():
    value = MesoscaleEnvironmentPhysics.vertical_velocity(100)
    assert value == 10


def test_stability_index():
    value = MesoscaleEnvironmentPhysics.stability_index(300, 290)
    assert value == 10


def test_mesoscale_energy():
    value = MesoscaleEnvironmentPhysics.mesoscale_energy(10, 20)
    assert value == 2000


def test_turbulence_factor():
    value = MesoscaleEnvironmentPhysics.turbulence_factor(20, 5)
    assert value == 4
