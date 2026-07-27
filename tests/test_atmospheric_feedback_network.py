from acf.model4d.physics.atmospheric_feedback_network import (
    AtmosphericFeedbackNetwork,
    FeedbackState
)


def create_state():

    return FeedbackState(
        temperature=300,
        humidity=12,
        cloud_cover=50,
        radiation=240,
        surface_temperature=302,
        ocean_temperature=301
    )


def test_moisture_feedback():

    model = AtmosphericFeedbackNetwork()

    assert model.moisture_feedback(create_state()) > 0



def test_radiative_feedback():

    model = AtmosphericFeedbackNetwork()

    assert model.radiative_feedback(create_state()) > 0



def test_cloud_feedback():

    model = AtmosphericFeedbackNetwork()

    assert model.cloud_feedback(create_state()) == 1.5



def test_temperature_feedback():

    model = AtmosphericFeedbackNetwork()

    assert model.temperature_feedback(create_state()) > 1



def test_surface_feedback():

    model = AtmosphericFeedbackNetwork()

    assert model.surface_feedback(create_state()) == 2



def test_ocean_atmosphere_feedback():

    model = AtmosphericFeedbackNetwork()

    assert model.ocean_atmosphere_feedback(create_state()) > 0



def test_feedback_equilibrium():

    model = AtmosphericFeedbackNetwork()

    result = model.feedback_equilibrium(create_state())

    assert result > 0
