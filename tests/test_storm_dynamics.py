from acf.model4d.physics.storm_dynamics import StormDynamicsPhysics


def test_cape():
    value = StormDynamicsPhysics.cape(4000, 3000)
    assert value == 1000


def test_cin():
    value = StormDynamicsPhysics.cin(150, 50)
    assert value == -100


def test_updraft_velocity():
    value = StormDynamicsPhysics.updraft_velocity(1000)
    assert value == 100


def test_wind_shear():
    value = StormDynamicsPhysics.wind_shear(20, 5)
    assert value == 15


def test_storm_intensity():
    value = StormDynamicsPhysics.storm_intensity(50, 2)
    assert value == 100


def test_supercell_potential():
    value = StormDynamicsPhysics.supercell_potential(200, 30)
    assert value == 6000


def test_storm_lifetime():
    value = StormDynamicsPhysics.storm_lifetime(120, 10)
    assert value == 12


def test_precipitation_efficiency():
    value = StormDynamicsPhysics.precipitation_efficiency(80, 100)
    assert value == 0.8


def test_vorticity():
    value = StormDynamicsPhysics.vorticity(20, 10)
    assert value == 2


def test_convective_index():
    value = StormDynamicsPhysics.convective_index(300, 250)
    assert value == 50
