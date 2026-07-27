from acf.model4d.physics.atmospheric_convection_dynamics import (
    AtmosphericConvectionDynamics,
    ConvectionState,
)


def test_buoyancy_force():

    model = AtmosphericConvectionDynamics()

    state = ConvectionState(
        surface_temperature_anomaly=2,
        lapse_rate=3,
        stability_index=1,
        moisture_content=1
    )

    assert model.buoyancy_force(state) == 6



def test_vertical_velocity():

    model = AtmosphericConvectionDynamics()

    state = ConvectionState(
        surface_temperature_anomaly=2,
        lapse_rate=3,
        stability_index=0.5,
        moisture_content=1
    )

    assert model.vertical_velocity(state) == 3



def test_convection_feedback():

    model = AtmosphericConvectionDynamics()

    state = ConvectionState(
        surface_temperature_anomaly=2,
        lapse_rate=2,
        stability_index=0.5,
        moisture_content=2,
        convection_efficiency=1
    )

    assert model.convection_feedback(state) == 4



def test_convection_state():

    model = AtmosphericConvectionDynamics()

    state = ConvectionState(
        surface_temperature_anomaly=3,
        lapse_rate=2,
        stability_index=1,
        moisture_content=1
    )

    assert model.convection_state(state) == "active_convection"
