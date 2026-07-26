from acf.model4d.physics.convection import Convection
import pytest


def test_buoyancy_positive():

    value = Convection.buoyancy(
        temperature_parcel=300,
        temperature_environment=290,
    )

    assert value > 0



def test_buoyancy_negative():

    value = Convection.buoyancy(
        temperature_parcel=280,
        temperature_environment=290,
    )

    assert value < 0



def test_buoyancy_invalid_temperature():

    with pytest.raises(ValueError):
        Convection.buoyancy(
            300,
            0
        )



def test_convective_velocity():

    value = Convection.convective_velocity(
        buoyancy=0.5,
        height=100
    )

    assert round(value, 2) == 10.0



def test_zero_velocity():

    value = Convection.convective_velocity(
        buoyancy=-1,
        height=100
    )

    assert value == 0.0



def test_negative_height():

    with pytest.raises(ValueError):
        Convection.convective_velocity(
            1,
            -10
        )



def test_instability():

    value = Convection.instability_index(
        300,
        280
    )

    assert value == 20



def test_stable_layer():

    value = Convection.instability_index(
        270,
        280
    )

    assert value == -10



def test_class_exists():

    assert Convection is not None



def test_gravity_constant():

    assert Convection.GRAVITY == 9.81
