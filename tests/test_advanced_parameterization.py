import pytest

from acf.model4d.physics.advanced_parameterization import (
    AdvancedParameterizationPhysics
)


def test_turbulence_closure():

    value = AdvancedParameterizationPhysics.turbulence_closure(
        0.4
    )

    assert round(value, 2) == 0.60



def test_cloud_parameterization():

    value = AdvancedParameterizationPhysics.cloud_parameterization(
        0.5
    )

    assert round(value, 2) == 0.40



def test_convection_adjustment():

    value = AdvancedParameterizationPhysics.convection_adjustment(
        4
    )

    assert value == 2



def test_boundary_layer():

    value = AdvancedParameterizationPhysics.boundary_layer_parameterization(
        10,
        0.5
    )

    assert round(value, 2) == 4.05



def test_stable():

    result = AdvancedParameterizationPhysics.stability_correction(
        0.5
    )

    assert result == "stable"



def test_neutral():

    result = AdvancedParameterizationPhysics.stability_correction(
        0.1
    )

    assert result == "neutral"



def test_unstable():

    result = AdvancedParameterizationPhysics.stability_correction(
        -0.1
    )

    assert result == "unstable"



def test_invalid_coefficient():

    with pytest.raises(ValueError):

        AdvancedParameterizationPhysics.turbulence_closure(
            0
        )



def test_invalid_cloud():

    with pytest.raises(ValueError):

        AdvancedParameterizationPhysics.cloud_parameterization(
            1.5
        )



def test_invalid_wind():

    with pytest.raises(ValueError):

        AdvancedParameterizationPhysics.boundary_layer_parameterization(
            -1,
            0.2
        )
