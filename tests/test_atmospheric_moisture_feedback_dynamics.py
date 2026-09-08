from acf.model4d.physics.atmospheric_moisture_feedback_dynamics import (
    AtmosphericMoistureFeedbackDynamics,
    MoistureFeedbackState,
)


def test_evaporation_feedback():

    model = AtmosphericMoistureFeedbackDynamics()

    state = MoistureFeedbackState(temperature_anomaly=2, ocean_evaporation=3, humidity_level=1, cloud_response=1)

    assert model.evaporation_feedback(state) == 6


def test_humidity_amplification():

    model = AtmosphericMoistureFeedbackDynamics()

    state = MoistureFeedbackState(temperature_anomaly=2, ocean_evaporation=3, humidity_level=0.5, cloud_response=1)

    assert model.humidity_amplification(state) == 3


def test_greenhouse_feedback():

    model = AtmosphericMoistureFeedbackDynamics()

    state = MoistureFeedbackState(
        temperature_anomaly=2, ocean_evaporation=2, humidity_level=1, cloud_response=0.5, greenhouse_effect=2
    )

    assert model.greenhouse_feedback(state) == 4


def test_moisture_state():

    model = AtmosphericMoistureFeedbackDynamics()

    state = MoistureFeedbackState(temperature_anomaly=1, ocean_evaporation=2, humidity_level=1, cloud_response=1)

    assert model.moisture_state(state) == "humidifying_feedback"
