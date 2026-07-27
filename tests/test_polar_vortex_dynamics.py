from acf.model4d.physics.polar_vortex_dynamics import (
    PolarVortexDynamics,
    PolarVortexState
)


def test_model_creation():

    model = PolarVortexDynamics()

    assert model.name == "Polar Vortex Dynamics"


def test_strength():

    model = PolarVortexDynamics()

    value = model.calculate_vortex_strength(
        50,
        20
    )

    assert value == 10


def test_stable_vortex():

    model = PolarVortexDynamics()

    assert (
        model.diagnose_stability(6)
        ==
        "stable"
    )


def test_moderate_vortex():

    model = PolarVortexDynamics()

    assert (
        model.diagnose_stability(3)
        ==
        "moderate"
    )


def test_weak_vortex():

    model = PolarVortexDynamics()

    assert (
        model.diagnose_stability(1)
        ==
        "weak"
    )


def test_ssw_effect():

    model = PolarVortexDynamics()

    result = model.sudden_stratospheric_warming_effect(
        10
    )

    assert result < 1


def test_simulation():

    model = PolarVortexDynamics()

    state = PolarVortexState(
        wind_speed=40,
        temperature_gradient=15
    )

    result = model.simulate(state)

    assert (
        result["module"]
        ==
        "Polar Vortex Dynamics"
    )


def test_hemisphere():

    state = PolarVortexState(
        wind_speed=30,
        temperature_gradient=10,
        hemisphere="south"
    )

    assert state.hemisphere == "south"


def test_version():

    model = PolarVortexDynamics()

    assert model.version == "8.88"


def test_factory():

    from acf.model4d.physics.polar_vortex_dynamics import (
        create_polar_vortex_model
    )

    model = create_polar_vortex_model()

    assert isinstance(
        model,
        PolarVortexDynamics
    )
