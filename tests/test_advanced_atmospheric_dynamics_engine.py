from acf.model4d.physics.advanced_atmospheric_dynamics_engine import (
    AdvancedAtmosphericDynamicsEngine,
    AtmosphericDynamicsState,
)


def build_state():

    return AtmosphericDynamicsState(
        jet_stream_speed=120,
        vorticity=85,
        divergence=75,
        convergence=70,
        warm_advection=80,
        cold_advection=20,
        upper_troposphere_forcing=90,
        lower_troposphere_energy=85,
    )


def test_jet_stream():

    engine = AdvancedAtmosphericDynamicsEngine()

    assert (
        engine.jet_stream_analysis(build_state())
        ==
        54.0
    )


def test_vorticity():

    engine = AdvancedAtmosphericDynamicsEngine()

    assert (
        engine.vorticity_analysis(build_state())
        ==
        68.0
    )


def test_dynamic_lift():

    engine = AdvancedAtmosphericDynamicsEngine()

    assert (
        engine.dynamic_lift_index(build_state())
        ==
        78.33
    )


def test_regime():

    engine = AdvancedAtmosphericDynamicsEngine()

    assert (
        engine.circulation_regime(build_state())
        ==
        "ACTIVE_DYNAMIC_REGIME"
    )


def test_update():

    engine = AdvancedAtmosphericDynamicsEngine()

    result = engine.dynamics_update(
        build_state()
    )

    assert result["regime"] == "ACTIVE_DYNAMIC_REGIME"
