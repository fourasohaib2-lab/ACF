from acf.model4d.physics.atmospheric_feedback_dynamics import (
    AtmosphericFeedbackDynamics,
    AtmosphericFeedbackDynamicsState,
)


def create_state():

    return AtmosphericFeedbackDynamicsState(
        temperature=300,
        humidity=10,
        cloud_cover=20,
        radiation_flux=250,
        convection=2,
        precipitation=5,
        surface_energy=300,
    )


def test_humidity_temperature_coupling():

    model = AtmosphericFeedbackDynamics()

    assert (
        model.humidity_temperature_coupling(create_state())
        == 3.4
    )


def test_cloud_radiation_coupling():

    model = AtmosphericFeedbackDynamics()

    assert (
        model.cloud_radiation_coupling(create_state())
        == 242
    )


def test_convection_feedback():

    model = AtmosphericFeedbackDynamics()

    assert (
        model.convection_feedback(create_state())
        == 5.5
    )


def test_energy_transport_feedback():

    model = AtmosphericFeedbackDynamics()

    assert (
        model.energy_transport_feedback(create_state())
        == 42.5
    )


def test_feedback_growth_rate():

    model = AtmosphericFeedbackDynamics()

    assert (
        model.feedback_growth_rate(create_state())
        == 5.0
    )


def test_climate_feedback_dynamics_index():

    model = AtmosphericFeedbackDynamics()

    assert (
        model.climate_feedback_dynamics_index(create_state())
        == 5.9
    )
