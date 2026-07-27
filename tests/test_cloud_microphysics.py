from acf.model4d.physics.cloud_microphysics import CloudMicrophysicsPhysics


def test_saturation_vapor_pressure():

    value = CloudMicrophysicsPhysics.saturation_vapor_pressure(
        20
    )

    assert round(value, 2) == 23.37



def test_condensation_rate():

    value = CloudMicrophysicsPhysics.condensation_rate(
        10,
        8,
        0.5
    )

    assert value == 1



def test_cloud_water_content():

    value = CloudMicrophysicsPhysics.cloud_water_content(
        20,
        10
    )

    assert value == 2



def test_droplet_growth_rate():

    value = CloudMicrophysicsPhysics.droplet_growth_rate(
        100,
        2
    )

    assert value == 0.0002



def test_autoconversion_rate():

    value = CloudMicrophysicsPhysics.autoconversion_rate(
        5,
        2
    )

    assert value == 0.03



def test_accretion_rate():

    value = CloudMicrophysicsPhysics.accretion_rate(
        2,
        3,
        0.5
    )

    assert value == 3



def test_ice_nucleation_rate():

    value = CloudMicrophysicsPhysics.ice_nucleation_rate(
        -10,
        100
    )

    assert value == 0.1



def test_deposition_growth():

    value = CloudMicrophysicsPhysics.deposition_growth(
        10,
        20
    )

    assert value == 0.2



def test_precipitation_efficiency():

    value = CloudMicrophysicsPhysics.precipitation_efficiency(
        5,
        20
    )

    assert value == 0.25



def test_terminal_velocity_droplet():

    value = CloudMicrophysicsPhysics.terminal_velocity_droplet(
        0.01
    )

    assert value == 0.13
