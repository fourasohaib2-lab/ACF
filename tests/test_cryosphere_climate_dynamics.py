from acf.model4d.physics.cryosphere_climate_dynamics import (
    CryosphereClimateDynamics,
    CryosphereState,
)


def test_albedo_effect():

    model = CryosphereClimateDynamics()

    state = CryosphereState(ice_cover=0.6, snow_cover=0.2, temperature_anomaly=2, melting_rate=1)

    assert model.albedo_effect(state) == 0.8


def test_ice_loss():

    model = CryosphereClimateDynamics()

    state = CryosphereState(ice_cover=0.5, snow_cover=0.3, temperature_anomaly=2, melting_rate=1)

    assert model.ice_loss(state) == 2


def test_feedback():

    model = CryosphereClimateDynamics()

    state = CryosphereState(ice_cover=0.5, snow_cover=0.2, temperature_anomaly=2, melting_rate=1)

    assert model.climate_feedback(state) == 0.6


def test_melting_state():

    model = CryosphereClimateDynamics()

    state = CryosphereState(ice_cover=0.7, snow_cover=0.2, temperature_anomaly=3, melting_rate=1)

    assert model.cryosphere_state(state) == "melting"
