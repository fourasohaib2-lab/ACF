from acf.model4d.physics.atmospheric_convection_dynamics import (
    AtmosphericConvectionDynamics,
    ConvectionState,
)


def test_buoyancy():

    model = AtmosphericConvectionDynamics()

    state = ConvectionState(
        temperature_difference=20,
        lapse_rate=6.5,
        stability_threshold=1,
        vertical_velocity=5,
        moisture_content=0.8,
    )

    assert model.calculate_buoyancy(state) == 2.0



def test_convection_intensity():

    model = AtmosphericConvectionDynamics()

    state = ConvectionState(
        temperature_difference=10,
        lapse_rate=2,
        stability_threshold=1,
        vertical_velocity=5,
        moisture_content=0.5,
    )

    assert model.convection_intensity(state) == 5.0



def test_vertical_heat_transport():

    model = AtmosphericConvectionDynamics()

    state = ConvectionState(
        temperature_difference=10,
        lapse_rate=2,
        stability_threshold=1,
        vertical_velocity=5,
        moisture_content=0.5,
    )

    assert model.vertical_heat_transport(state) == 2.5



def test_unstable_convection():

    model = AtmosphericConvectionDynamics()

    state = ConvectionState(
        temperature_difference=30,
        lapse_rate=6,
        stability_threshold=1,
        vertical_velocity=10,
        moisture_content=1,
    )

    assert model.convection_state(state) == "unstable_convection"
