from acf.model4d.physics.atmospheric_feedback_network import AtmosphericFeedbackNetwork, AtmosphericFeedbackState


def create_state():

    return AtmosphericFeedbackState(
        temperature=300,
        humidity=10,
        cloud_cover=20,
        radiation_flux=250,
        convection=2,
        precipitation=5,
        surface_energy=300,
    )


def test_humidity_temperature_feedback():

    model = AtmosphericFeedbackNetwork()

    assert model.humidity_temperature_feedback(create_state()) == 3.4


def test_cloud_radiation_feedback():

    model = AtmosphericFeedbackNetwork()

    assert model.cloud_radiation_feedback(create_state()) == 242


def test_convection_moisture_feedback():

    model = AtmosphericFeedbackNetwork()

    assert model.convection_moisture_feedback(create_state()) == 4.5


def test_precipitation_energy_feedback():

    model = AtmosphericFeedbackNetwork()

    assert model.precipitation_energy_feedback(create_state()) == 32.5


def test_climate_feedback_index():

    model = AtmosphericFeedbackNetwork()

    assert model.climate_feedback_index(create_state()) == 15.0
