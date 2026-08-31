from acf.model4d.physics.atmospheric_wave_feedback_dynamics import (
    AtmosphericWaveFeedbackDynamics,
    AtmosphericWaveFeedbackState,
)


def test_wave_growth():

    model = AtmosphericWaveFeedbackDynamics()

    state = AtmosphericWaveFeedbackState(
        wave_amplitude=10, convective_energy=50, turbulence_level=20, stability_index=0.5
    )

    result = model.calculate_wave_growth(state)

    assert result > 10


def test_feedback_cycle():

    model = AtmosphericWaveFeedbackDynamics()

    state = AtmosphericWaveFeedbackState(
        wave_amplitude=5, convective_energy=40, turbulence_level=30, stability_index=0.4
    )

    result = model.calculate_feedback_cycle(state)

    assert result > 5


def test_stability():

    model = AtmosphericWaveFeedbackDynamics()

    unstable = AtmosphericWaveFeedbackState(
        wave_amplitude=1, convective_energy=1, turbulence_level=1, stability_index=0.1
    )

    assert model.stability_response(unstable) == "unstable"


def test_simulation():

    model = AtmosphericWaveFeedbackDynamics()

    state = AtmosphericWaveFeedbackState(
        wave_amplitude=20, convective_energy=80, turbulence_level=40, stability_index=0.8, region="polar"
    )

    result = model.simulate(state)

    assert result["module"] == "Atmospheric Wave Feedback Dynamics"
    assert result["region"] == "polar"
    assert "wave_growth" in result
