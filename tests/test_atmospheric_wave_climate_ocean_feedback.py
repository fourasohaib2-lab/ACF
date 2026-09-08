from acf.model4d.physics.atmospheric_wave_climate_ocean_feedback import (
    AtmosphericWaveClimateOceanFeedback,
    AtmosphericWaveClimateOceanState,
)


def test_creation():

    model = AtmosphericWaveClimateOceanFeedback()

    assert model.name == "Atmospheric Wave Climate Ocean Feedback"


def test_feedback():

    state = AtmosphericWaveClimateOceanState(wave_energy=20, ocean_temperature=25, climate_feedback=5)

    model = AtmosphericWaveClimateOceanFeedback()

    result = model.calculate_feedback(state)

    assert result > 0


def test_simulation():

    state = AtmosphericWaveClimateOceanState(
        wave_energy=30, ocean_temperature=20, climate_feedback=10, humidity_flux=5, ocean_current_strength=8
    )

    model = AtmosphericWaveClimateOceanFeedback()

    output = model.simulate(state)

    assert "feedback_index" in output
    assert "ocean_response" in output
    assert "wave_response" in output


def test_climate_state():

    model = AtmosphericWaveClimateOceanFeedback()

    assert model.climate_state(5) == "weak"
    assert model.climate_state(20) == "moderate"
    assert model.climate_state(50) == "strong"
