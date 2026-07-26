from acf.model4d.physics.aerosol_cloud_interaction import (
    AerosolCloudInteractionPhysics
)


def test_ccn_activation():

    value = AerosolCloudInteractionPhysics.ccn_activation(
        1000,
        10
    )

    assert round(value, 2) == 100


def test_droplet_number():

    value = AerosolCloudInteractionPhysics.droplet_number(
        1000,
        0.5
    )

    assert value == 500


def test_indirect_effect():

    value = AerosolCloudInteractionPhysics.aerosol_indirect_effect(
        0.5,
        0.6
    )

    assert round(value, 2) == 0.2


def test_cloud_albedo():

    value = AerosolCloudInteractionPhysics.cloud_albedo_response(
        1000
    )

    assert round(value, 2) == 0.5


def test_scavenging():

    value = AerosolCloudInteractionPhysics.aerosol_scavenging_rate(
        1000,
        5
    )

    assert value == 50


def test_cloud_lifetime():

    value = AerosolCloudInteractionPhysics.cloud_lifetime_change(
        10,
        20
    )

    assert value == 12


def test_negative_supersaturation():

    try:
        AerosolCloudInteractionPhysics.ccn_activation(
            1000,
            -1
        )
        assert False
    except ValueError:
        assert True


def test_invalid_efficiency():

    try:
        AerosolCloudInteractionPhysics.droplet_number(
            1000,
            2
        )
        assert False
    except ValueError:
        assert True


def test_invalid_albedo():

    try:
        AerosolCloudInteractionPhysics.aerosol_indirect_effect(
            0,
            1
        )
        assert False
    except ValueError:
        assert True


def test_invalid_loading():

    try:
        AerosolCloudInteractionPhysics.cloud_lifetime_change(
            10,
            -5
        )
        assert False
    except ValueError:
        assert True
