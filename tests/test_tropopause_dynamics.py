from acf.model4d.physics.tropopause_dynamics import (
    TropopauseDynamics,
    TropopauseState
)


def test_creation():

    model = TropopauseDynamics()

    assert model.name == "Tropopause Dynamics"



def test_layer():

    model = TropopauseDynamics()

    state = TropopauseState(
        temperature=-55,
        pressure=200,
        altitude=12000,
        lapse_rate=2
    )

    result = model.diagnose_layer(state)

    assert result["layer"] == "stratospheric"



def test_height():

    model = TropopauseDynamics()

    h = model.tropopause_height_estimate(
        0
    )

    assert h > 10000



def test_stability():

    model = TropopauseDynamics()

    value = model.stability_index(
        4
    )

    assert value > 0



def test_exchange():

    model = TropopauseDynamics()

    value = model.exchange_probability(
        10
    )

    assert 0 < value <= 1



def test_simulation():

    model = TropopauseDynamics()

    state = TropopauseState(
        temperature=-50,
        pressure=180,
        altitude=13000,
        lapse_rate=3,
        latitude=45
    )

    result = model.simulate(state)

    assert "stability" in result
    assert "exchange" in result



def test_latitude():

    model = TropopauseDynamics()

    pole = model.tropopause_height_estimate(
        90
    )

    assert pole < 12000



def test_equator():

    model = TropopauseDynamics()

    equator = model.tropopause_height_estimate(
        0
    )

    assert equator == 17000



def test_object():

    state = TropopauseState(
        temperature=-60,
        pressure=150,
        altitude=15000,
        lapse_rate=2
    )

    assert state.altitude == 15000



def test_version():

    model = TropopauseDynamics()

    assert model.version == "1.0"
