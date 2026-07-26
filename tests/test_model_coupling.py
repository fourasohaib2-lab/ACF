import pytest

from acf.model4d.physics.model_coupling import (
    ModelCouplingPhysics
)


def test_coupling_strength():

    value = ModelCouplingPhysics.coupling_strength(
        0.8,
        0.7,
        0.6
    )

    assert value == 0.7



def test_energy_exchange():

    value = ModelCouplingPhysics.energy_exchange(
        10,
        8
    )

    assert value == 2



def test_balance():

    result = ModelCouplingPhysics.coupling_balance(
        1.0,
        1.02
    )

    assert result == "balanced"



def test_atmosphere_dominant():

    result = ModelCouplingPhysics.coupling_balance(
        2,
        1
    )

    assert result == "atmosphere_dominant"



def test_feedback():

    value = ModelCouplingPhysics.feedback_factor(
        100,
        110
    )

    assert value == 0.1



def test_climate_index():

    value = ModelCouplingPhysics.climate_system_index(
        1,
        1,
        1,
        1
    )

    assert value == 1



def test_negative_error():

    with pytest.raises(ValueError):

        ModelCouplingPhysics.coupling_strength(
            -1,
            1,
            1
        )



def test_zero_total():

    with pytest.raises(ValueError):

        ModelCouplingPhysics.coupling_strength(
            0,
            0,
            0
        )



def test_feedback_error():

    with pytest.raises(ValueError):

        ModelCouplingPhysics.feedback_factor(
            0,
            10
        )



def test_flux_error():

    with pytest.raises(ValueError):

        ModelCouplingPhysics.energy_exchange(
            -1,
            2
        )

