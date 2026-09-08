from acf.model4d.physics.cloud_dynamics_advanced import CloudDynamicsAdvancedPhysics


def test_updraft_velocity():

    value = CloudDynamicsAdvancedPhysics.updraft_velocity(1, 10)

    assert value == 4.47214


def test_downdraft_velocity():

    value = CloudDynamicsAdvancedPhysics.downdraft_velocity(-1, 10)

    assert value == 4.47214


def test_entrainment_rate():

    value = CloudDynamicsAdvancedPhysics.entrainment_rate(10, 5)

    assert value == 2


def test_detrainment_rate():

    value = CloudDynamicsAdvancedPhysics.detrainment_rate(20, 10)

    assert value == 2


def test_turbulence_mixing():

    value = CloudDynamicsAdvancedPhysics.turbulence_mixing(2, 5)

    assert value == 10


def test_cloud_lifetime():

    value = CloudDynamicsAdvancedPhysics.cloud_lifetime(20, 5)

    assert value == 4


def test_cape():

    value = CloudDynamicsAdvancedPhysics.convective_available_energy(2, 100)

    assert value == 1962


def test_cin():

    value = CloudDynamicsAdvancedPhysics.convective_inhibition(2, 100)

    assert value == 1962


def test_plume_temperature():

    value = CloudDynamicsAdvancedPhysics.plume_temperature(300, 0.006, 1000)

    assert value == 294


def test_cloud_top_height():

    value = CloudDynamicsAdvancedPhysics.cloud_top_height(6, 0.006)

    assert value == 1000
