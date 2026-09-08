from acf.model4d.physics.cloud_atmosphere_interaction import CloudAtmosphereInteraction, CloudAtmosphereState


def create_state():
    return CloudAtmosphereState(
        temperature=280,
        pressure=85000,
        humidity=12,
        cloud_water=3,
        cloud_ice=2,
        vertical_velocity=5,
        radiation_flux=250,
        precipitation=1,
    )


def test_saturation_adjustment():

    model = CloudAtmosphereInteraction()

    assert model.saturation_adjustment(create_state()) == 12.55


def test_condensation_process():

    model = CloudAtmosphereInteraction()

    assert model.condensation_process(create_state()) == 6.5


def test_evaporation_process():

    model = CloudAtmosphereInteraction()

    assert model.evaporation_process(create_state()) == 1.14


def test_cloud_growth_rate():

    model = CloudAtmosphereInteraction()

    assert model.cloud_growth_rate(create_state()) == 3.8


def test_precipitation_efficiency():

    model = CloudAtmosphereInteraction()

    assert model.precipitation_efficiency(create_state()) == 20.0


def test_cloud_radiative_feedback():

    model = CloudAtmosphereInteraction()

    assert model.cloud_radiative_feedback(create_state()) == 242
