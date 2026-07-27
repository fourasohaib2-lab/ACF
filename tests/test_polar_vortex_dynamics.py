"""
Tests for Polar Vortex Dynamics
"""

from acf.model4d.physics.polar_vortex_dynamics import (
    PolarVortexDynamics,
    PolarVortexState,
)


def test_creation():

    state = PolarVortexState(
        wind_speed=40,
        temperature_gradient=15
    )

    assert state.wind_speed == 40
    assert state.temperature_gradient == 15


def test_default_stability():

    state = PolarVortexState(
        wind_speed=40,
        temperature_gradient=15
    )

    assert state.stability_index == 1.0


def test_simulation():

    model = PolarVortexDynamics()

    state = PolarVortexState(
        wind_speed=40,
        temperature_gradient=15
    )

    result = model.simulate(state)

    assert result["name"] == "Polar Vortex Dynamics"
    assert result["intensity"] == 600
    assert result["status"] == "strong"


def test_hemisphere():

    state = PolarVortexState(
        wind_speed=30,
        temperature_gradient=10,
        hemisphere="south"
    )

    model = PolarVortexDynamics()

    result = model.hemisphere_effect(state)

    assert result == "Antarctic polar vortex"


def test_custom_stability():

    state = PolarVortexState(
        wind_speed=20,
        temperature_gradient=10,
        stability_index=2
    )

    assert state.stability_index == 2


def test_weak_vortex():

    model = PolarVortexDynamics()

    state = PolarVortexState(
        wind_speed=5,
        temperature_gradient=5
    )

    result = model.simulate(state)

    assert result["status"] == "weak"


def test_moderate_vortex():

    model = PolarVortexDynamics()

    state = PolarVortexState(
        wind_speed=20,
        temperature_gradient=15
    )

    result = model.simulate(state)

    assert result["status"] == "moderate"


def test_version():

    model = PolarVortexDynamics()

    assert model.version == "1.0"


def test_name():

    model = PolarVortexDynamics()

    assert model.name == "Polar Vortex Dynamics"


def test_state_structure():

    state = PolarVortexState(
        wind_speed=50,
        temperature_gradient=20
    )

    assert hasattr(state, "stability_index")
