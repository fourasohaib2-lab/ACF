"""
Atmospheric Complexity Framework (ACF)

AI Forecasting Framework Test Suite (MISSION ACF-028)
"""

from acf.ai.decision_support.decision_engine import ForecastDecisionEngine
from acf.ai.ensemble.ensemble_manager import EnsembleManager
from acf.ai.neural_models.models import NEURAL_MODELS_REGISTRY, NeuralWeatherModelEngine
from acf.ai.physics_informed.pde_constraints import PDEPhysicsLossEvaluator
from acf.ai.uncertainty.uncertainty_engine import UncertaintyQuantificationEngine
from acf.science.query_engine import ScientificQueryEngine


def test_neural_weather_models_registry():
    """Test du registre des modèles d'IA météorologiques."""
    assert len(NEURAL_MODELS_REGISTRY) >= 7

    graphcast = NeuralWeatherModelEngine.get_model("graphcast")
    assert graphcast is not None
    assert "GNN" in graphcast.architecture
    assert graphcast.max_lead_time_days == 10

    arome_ai = NeuralWeatherModelEngine.get_model("arome_ai")
    assert arome_ai is not None
    assert arome_ai.spatial_resolution_deg == 0.025


def test_pde_physics_loss_evaluator():
    """Test des résidus de pertes physiques PDE."""
    l_mass = PDEPhysicsLossEvaluator.mass_conservation_residual(div_wind=0.01)
    assert abs(l_mass - 0.01) < 1e-5

    l_moist = PDEPhysicsLossEvaluator.moisture_conservation_residual(dq_dt=0.05, advection_q=-0.05)
    assert abs(l_moist) < 1e-5

    losses = PDEPhysicsLossEvaluator.evaluate_total_physics_loss(
        {
            "divergence_wind": 0.001,
            "dq_dt": 0.01,
            "adv_q": -0.01,
            "u": 10.0,
            "u_geo": 10.0,
        }
    )
    assert losses["is_physically_consistent"] is True


def test_ensemble_manager():
    """Test du gestionnaire statistique d'ensemble."""
    members = [280.0, 282.0, 285.0, 288.0, 290.0]
    ens = EnsembleManager(members)

    assert abs(ens.mean - 285.0) < 1e-4
    assert abs(ens.median - 285.0) < 1e-4
    assert ens.spread > 3.0

    prob_rain = ens.probability_exceedance(285.0)
    assert abs(prob_rain - 0.6) < 1e-4

    brier = ens.brier_score(285.0, observed_event=True)
    assert brier < 0.25

    crps = ens.crps(285.0)
    assert crps > 0.0


def test_uncertainty_quantification_engine():
    """Test du moteur de quantification de l'incertitude."""
    preds = [25.0, 26.0, 24.5, 25.5, 24.0]
    res = UncertaintyQuantificationEngine.decompose_uncertainty(preds)

    assert abs(res["mean"] - 25.0) < 1e-4
    assert res["epistemic_std"] > 0.0
    assert 0.0 <= res["confidence_score"] <= 1.0

    low, high = UncertaintyQuantificationEngine.calculate_confidence_interval(mean=25.0, std=1.0)
    assert low < 25.0 < high


def test_forecast_decision_engine():
    """Test du moteur de décision opérationnelle et d'évaluation des risques."""
    engine = ForecastDecisionEngine()
    state = {
        "CAPE": 2500.0,
        "shear_0_6km": 20.0,
        "EHI": 1.5,
        "IVT": 600.0,
        "wind_gust_ms": 30.0,
    }
    assessment = engine.assess_severe_weather_risk(state)

    assert assessment["risk_level"] in ["ÉLEVÉ", "CRITIQUE / EXTRÊME"]
    assert len(assessment["detected_phenomena"]) >= 2
    assert "Supercellules" in assessment["detected_phenomena"][0] or "Grêle" in assessment["detected_phenomena"][0]
    assert len(assessment["operational_warnings"]) >= 1


def test_query_engine_phase14_ai_questions():
    """Test le ScientificQueryEngine sur les questions d'IA météorologique de la mission ACF-028."""
    q_engine = ScientificQueryEngine()

    # 1. Why does AI predict heavy rain?
    r1 = q_engine.ask("Why does AI predict heavy rain?")
    assert "causal_chain" in r1
    assert any("PWV" in v or "CAPE" in v for v in r1["key_variables"])

    # 2. Why is confidence low?
    r2 = q_engine.ask("Why is confidence low?")
    assert "uncertainty_metrics" in r2
    assert "Epistemic Uncertainty" in r2["uncertainty_metrics"]

    # 3. Compare GraphCast and IFS
    r3 = q_engine.ask("Compare GraphCast and IFS")
    assert "comparison_table" in r3
    assert "GraphCast (IA)" in r3["comparison_table"]

    # 4. Explain ensemble spread
    r4 = q_engine.ask("Explain ensemble spread")
    assert "equation" in r4

    # 5. Explain severe weather risk
    r5 = q_engine.ask("Explain severe weather risk")
    assert "risk_indices" in r5
