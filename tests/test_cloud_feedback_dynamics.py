from acf.model4d.physics.cloud_feedback_dynamics import (
    CloudFeedbackDynamics,
    CloudState,
)


def test_cloud_formation():

    model = CloudFeedbackDynamics()

    state = CloudState(
        humidity=0.8,
        convection_strength=5,
        cloud_fraction=0.5,
        solar_reflection=10,
        infrared_trapping=20,
    )

    assert model.cloud_formation(state) == 4.0


def test_albedo_effect():

    model = CloudFeedbackDynamics()

    state = CloudState(
        humidity=1,
        convection_strength=2,
        cloud_fraction=0.5,
        solar_reflection=10,
        infrared_trapping=20,
    )

    assert model.albedo_effect(state) == 5.0


def test_greenhouse_cloud_effect():

    model = CloudFeedbackDynamics()

    state = CloudState(
        humidity=1,
        convection_strength=2,
        cloud_fraction=0.5,
        solar_reflection=10,
        infrared_trapping=20,
    )

    assert model.greenhouse_cloud_effect(state) == 10.0


def test_positive_feedback():

    model = CloudFeedbackDynamics()

    state = CloudState(
        humidity=1,
        convection_strength=3,
        cloud_fraction=0.8,
        solar_reflection=5,
        infrared_trapping=20,
    )

    assert model.feedback_state(state) == "positive_cloud_feedback"
