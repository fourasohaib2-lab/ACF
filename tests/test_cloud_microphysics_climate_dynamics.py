from acf.model4d.physics.cloud_microphysics_climate_dynamics import (
    CloudMicrophysicsClimateDynamics,
    CloudMicrophysicsState,
)


def test_condensation():

    model = CloudMicrophysicsClimateDynamics()

    state = CloudMicrophysicsState(
        temperature_anomaly=2,
        humidity=4,
        condensation_rate=0.5,
        cloud_fraction=1
    )

    assert model.condensation(state) == 2



def test_cloud_formation():

    model = CloudMicrophysicsClimateDynamics()

    state = CloudMicrophysicsState(
        temperature_anomaly=2,
        humidity=4,
        condensation_rate=0.5,
        cloud_fraction=0.5
    )

    assert model.cloud_formation(state) == 1



def test_radiative_feedback():

    model = CloudMicrophysicsClimateDynamics()

    state = CloudMicrophysicsState(
        temperature_anomaly=1,
        humidity=4,
        condensation_rate=0.5,
        cloud_fraction=0.5,
        radiative_effect=2
    )

    assert model.radiative_feedback(state) == 2



def test_cloud_state():

    model = CloudMicrophysicsClimateDynamics()

    state = CloudMicrophysicsState(
        temperature_anomaly=1,
        humidity=2,
        condensation_rate=1,
        cloud_fraction=1
    )

    assert model.cloud_state(state) == "active_cloud_feedback"
