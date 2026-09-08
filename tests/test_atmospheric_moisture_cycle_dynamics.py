from acf.model4d.physics.atmospheric_moisture_cycle_dynamics import (
    AtmosphericMoistureCycleDynamics,
    MoistureCycleState,
)


def create_state():

    return MoistureCycleState(
        evaporation_rate=5,
        atmospheric_humidity=2,
        temperature=20,
        condensation_rate=0.5,
        cloud_fraction=0.8,
        precipitation_rate=10,
    )


def test_evaporation_flux():

    model = AtmosphericMoistureCycleDynamics()

    assert model.evaporation_flux(create_state()) == 6.0


def test_moisture_transport():

    model = AtmosphericMoistureCycleDynamics()

    assert model.moisture_transport(create_state()) == 1.6


def test_condensation_process():

    model = AtmosphericMoistureCycleDynamics()

    assert model.condensation_process(create_state()) == 1.0


def test_cloud_formation():

    model = AtmosphericMoistureCycleDynamics()

    assert model.cloud_formation(create_state()) == 0.4


def test_precipitation_generation():

    model = AtmosphericMoistureCycleDynamics()

    assert model.precipitation_generation(create_state()) == 8.0


def test_hydrological_feedback():

    model = AtmosphericMoistureCycleDynamics()

    assert model.hydrological_feedback(create_state()) == 1.38
