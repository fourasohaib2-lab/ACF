from acf.model4d.physics.jet_stream_dynamics import (
    JetStreamState,
    JetStreamDynamics
)


def create_model():

    state = JetStreamState(
        wind_speed=60.0,
        temperature_gradient=0.8,
        vertical_shear=0.4,
        latitude=45.0
    )

    return JetStreamDynamics(state)



def test_state_creation():

    model = create_model()

    assert model.state.wind_speed == 60.0



def test_coriolis():

    model = create_model()

    value = model.coriolis_parameter()

    assert value > 0



def test_thermal_balance():

    model = create_model()

    assert model.thermal_wind_balance() > 0



def test_jet_intensity():

    model = create_model()

    assert model.jet_intensity() > 0



def test_blocking_risk():

    model = create_model()

    risk = model.blocking_risk()

    assert 0 <= risk <= 1



def test_diagnostic():

    model = create_model()

    data = model.diagnostic()

    assert "jet_intensity" in data



def test_high_wind():

    state = JetStreamState(
        100,
        1,
        0.5,
        50
    )

    model = JetStreamDynamics(state)

    assert model.jet_intensity() > 0



def test_equator_coriolis():

    state = JetStreamState(
        40,
        0.5,
        0.2,
        0
    )

    model = JetStreamDynamics(state)

    assert abs(model.coriolis_parameter()) < 1e-8



def test_negative_gradient():

    state = JetStreamState(
        40,
        -0.5,
        0.3,
        40
    )

    model = JetStreamDynamics(state)

    assert isinstance(
        model.thermal_wind_balance(),
        float
    )



def test_complete_execution():

    model = create_model()

    result = model.diagnostic()

    assert len(result) == 5
