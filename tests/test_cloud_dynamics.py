from acf.model4d.physics.cloud_dynamics import CloudDynamicsPhysics


def test_updraft_velocity():

    value = CloudDynamicsPhysics.updraft_velocity(
        0.5,
        1000
    )

    assert round(value, 2) == 3.16



def test_downdraft_velocity():

    value = CloudDynamicsPhysics.downdraft_velocity(
        0.5,
        1000
    )

    assert round(value, 2) == -3.16



def test_cloud_thickness():

    value = CloudDynamicsPhysics.cloud_thickness(
        5000,
        1000
    )

    assert value == 4000



def test_entrainment_rate():

    value = CloudDynamicsPhysics.entrainment_rate(
        1.5,
        1
    )

    assert value == 0.5



def test_detrainment_rate():

    value = CloudDynamicsPhysics.detrainment_rate(
        100,
        20
    )

    assert value == 0.2



def test_cloud_growth():

    value = CloudDynamicsPhysics.cloud_growth(
        100,
        20
    )

    assert value == 120



def test_precipitation_efficiency():

    value = CloudDynamicsPhysics.precipitation_efficiency(
        50,
        100
    )

    assert value == 0.5



def test_cloud_mass_flux():

    value = CloudDynamicsPhysics.cloud_mass_flux(
        1,
        10,
        5
    )

    assert value == 50



def test_invalid_cloud():

    try:
        CloudDynamicsPhysics.cloud_thickness(
            100,
            500
        )
        assert False
    except ValueError:
        assert True



def test_invalid_mass():

    try:
        CloudDynamicsPhysics.cloud_mass_flux(
            -1,
            10,
            5
        )
        assert False
    except ValueError:
        assert True
