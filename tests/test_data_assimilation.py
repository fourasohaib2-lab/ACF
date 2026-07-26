from acf.model4d.physics.data_assimilation import (
    DataAssimilationPhysics
)

import pytest


def test_innovation():

    value = DataAssimilationPhysics.innovation(
        12,
        10
    )

    assert value == 2



def test_weight():

    value = DataAssimilationPhysics.observation_weight(
        2
    )

    assert value == 0.25



def test_kalman_gain():

    value = DataAssimilationPhysics.kalman_gain(
        4,
        1
    )

    assert round(value,2) == 0.80



def test_analysis_update():

    value = DataAssimilationPhysics.analysis_update(
        10,
        20,
        0.5
    )

    assert value == 15



def test_cost():

    value = DataAssimilationPhysics.four_d_var_cost(
        2,
        3
    )

    assert value == 13



def test_quality():

    value = DataAssimilationPhysics.quality_index(
        0
    )

    assert value == 1



def test_spread():

    value = DataAssimilationPhysics.spread(
        9
    )

    assert value == 3



def test_negative_error():

    with pytest.raises(ValueError):

        DataAssimilationPhysics.quality_index(
            -1
        )



def test_zero_error():

    with pytest.raises(ValueError):

        DataAssimilationPhysics.observation_weight(
            0
        )



def test_invalid_gain():

    with pytest.raises(ValueError):

        DataAssimilationPhysics.analysis_update(
            1,
            2,
            2
        )
