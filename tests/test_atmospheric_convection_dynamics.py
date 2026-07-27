from acf.model4d.physics.atmospheric_convection_dynamics import (
    AtmosphericConvectionDynamics,
    ConvectionState,
)



def test_buoyancy():

    model = AtmosphericConvectionDynamics()

    state = ConvectionState(
        temperature_anomaly=20,
        lapse_rate=6.5,
        environmental_lapse_rate=9,
        moisture_content=0.8,
        vertical_velocity=5,
    )

    assert model.calculate_buoyancy(state) == 2.0



def test_instability_index():

    model = AtmosphericConvectionDynamics()

    state = ConvectionState(
        temperature_anomaly=10,
        lapse_rate=6,
        environmental_lapse_rate=9,
        moisture_content=0.5,
        vertical_velocity=4,
    )

    assert model.instability_index(state) == 3



def test_convective_energy():

    model = AtmosphericConvectionDynamics()

    state = ConvectionState(
        temperature_anomaly=20,
        lapse_rate=6,
        environmental_lapse_rate=8,
        moisture_content=0.5,
        vertical_velocity=5,
    )

    assert model.convective_energy(state) == 1.0



def test_heat_transport():

    model = AtmosphericConvectionDynamics()

    state = ConvectionState(
        temperature_anomaly=10,
        lapse_rate=6,
        environmental_lapse_rate=7,
        moisture_content=0.5,
        vertical_velocity=10,
    )

    assert model.vertical_heat_transport(state) == 2.5



def test_unstable_convection():

    model = AtmosphericConvectionDynamics()

    state = ConvectionState(
        temperature_anomaly=30,
        lapse_rate=5,
        environmental_lapse_rate=8,
        moisture_content=1,
        vertical_velocity=10,
    )

    assert (
        model.convection_state(state)
        ==
        "unstable_convection"
    )



def test_stable_atmosphere():

    model = AtmosphericConvectionDynamics()

    state = ConvectionState(
        temperature_anomaly=1,
        lapse_rate=8,
        environmental_lapse_rate=6,
        moisture_content=0.2,
        vertical_velocity=1,
    )

    assert (
        model.convection_state(state)
        ==
        "stable_atmosphere"
    )
