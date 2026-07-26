import pytest

from acf.model4d.physics.boundary_layer import BoundaryLayerPhysics


def test_pbl_height():

    value = BoundaryLayerPhysics.pbl_height(
        0.25
    )

    assert value == 500.0



def test_mixing_length():

    value = BoundaryLayerPhysics.mixing_length(
        100
    )

    assert value == 10.0



def test_turbulent_diffusion():

    value = BoundaryLayerPhysics.turbulent_diffusion(
        5
    )

    assert value == 2.0



def test_stable_layer():

    result = BoundaryLayerPhysics.stability_parameter(
        0.1
    )

    assert result == "stable"



def test_unstable_layer():

    result = BoundaryLayerPhysics.stability_parameter(
        -0.1
    )

    assert result == "unstable"



def test_neutral_layer():

    result = BoundaryLayerPhysics.stability_parameter(
        0
    )

    assert result == "neutral"



def test_friction_velocity():

    value = BoundaryLayerPhysics.friction_velocity(
        4
    )

    assert value == 0.1



def test_negative_gradient():

    with pytest.raises(ValueError):

        BoundaryLayerPhysics.pbl_height(
            -1
        )



def test_negative_wind():

    with pytest.raises(ValueError):

        BoundaryLayerPhysics.turbulent_diffusion(
            -5
        )



def test_zero_height():

    with pytest.raises(ValueError):

        BoundaryLayerPhysics.mixing_length(
            0
        )
