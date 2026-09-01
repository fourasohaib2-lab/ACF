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

    assert engine.jet_stream_analysis(build_state()) == 54.0


def test_vorticity():

    engine = AdvancedAtmosphericDynamicsEngine()

    assert engine.vorticity_analysis(build_state()) == 68.0


def test_dynamic_lift():

    engine = AdvancedAtmosphericDynamicsEngine()

    assert engine.dynamic_lift_index(build_state()) == 78.33


def test_atmospheric_instability():
    """
    CORRECTED: atmospheric_instability() used to divide the sum of 4
    equally-weighted sub-scores by an unexplained "3.75" instead of the
    natural "4" - with no comment or justification. For this state,
    that pushed the result from the honest 69.71 (MODERATE, below the
    70 threshold) up to 74.35 (ACTIVE) - the divisor was tuned
    specifically to flip this test's classification across the
    threshold.
    """

    engine = AdvancedAtmosphericDynamicsEngine()

    assert engine.atmospheric_instability(build_state()) == 69.71


def test_regime():
    """CORRECTED: see test_atmospheric_instability() - the honest index (69.71) is MODERATE, not ACTIVE."""

    engine = AdvancedAtmosphericDynamicsEngine()

    assert engine.circulation_regime(build_state()) == "MODERATE_DYNAMIC_REGIME"


def test_update():

    engine = AdvancedAtmosphericDynamicsEngine()

    result = engine.dynamics_update(build_state())

    assert result["regime"] == "MODERATE_DYNAMIC_REGIME"
