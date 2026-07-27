from acf.model4d.physics.atmospheric_wave_climate_interaction import (
    AtmosphericWaveClimateInteraction,
    AtmosphericWaveClimateState,
)


def test_wave_energy():

    model = AtmosphericWaveClimateInteraction()

    state = AtmosphericWaveClimateState(
        wave_amplitude=4,
        wave_frequency=2,
        ocean_temperature_anomaly=1,
        climate_feedback_strength=3,
    )

    energy = model.compute_wave_energy(state)

    assert energy == 16


def test_ocean_feedback():

    model = AtmosphericWaveClimateInteraction()

    state = AtmosphericWaveClimateState(
        wave_amplitude=2,
        wave_frequency=1,
        ocean_temperature_anomaly=2,
        climate_feedback_strength=5,
    )

    feedback = model.compute_ocean_feedback(state)

    assert feedback == 10


def test_climate_response():

    model = AtmosphericWaveClimateInteraction()

    state = AtmosphericWaveClimateState(
        wave_amplitude=3,
        wave_frequency=2,
        ocean_temperature_anomaly=2,
        climate_feedback_strength=4,
    )

    result = model.compute_climate_response(state)

    assert "total_feedback" in result


def test_classification():

    model = AtmosphericWaveClimateInteraction()

    state = AtmosphericWaveClimateState(
        wave_amplitude=5,
        wave_frequency=2,
        ocean_temperature_anomaly=3,
        climate_feedback_strength=2,
    )

    regime = model.classify_interaction(state)

    assert regime == "strong_positive_feedback"
