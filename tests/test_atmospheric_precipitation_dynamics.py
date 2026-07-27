from acf.model4d.physics.atmospheric_precipitation_dynamics import (
    AtmosphericPrecipitationDynamics,
    PrecipitationState,
)


def test_condensation_amount():

    model = AtmosphericPrecipitationDynamics()

    state = PrecipitationState(
        humidity=10,
        condensation_rate=0.5,
        convection_intensity=1
    )

    assert model.condensation_amount(state) == 5



def test_precipitation_rate():

    model = AtmosphericPrecipitationDynamics()

    state = PrecipitationState(
        humidity=10,
        condensation_rate=0.5,
        convection_intensity=2,
        precipitation_efficiency=0.5
    )

    assert model.precipitation_rate(state) == 5



def test_precipitation_efficiency():

    model = AtmosphericPrecipitationDynamics()

    state = PrecipitationState(
        humidity=20,
        condensation_rate=0.5,
        convection_intensity=1,
        precipitation_efficiency=0.5
    )

    assert model.precipitation_rate(state) == 5



def test_water_state():

    model = AtmosphericPrecipitationDynamics()

    state = PrecipitationState(
        humidity=5,
        condensation_rate=1,
        convection_intensity=1
    )

    assert model.water_state(state) == "active_precipitation"
