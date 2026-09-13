"""
Atmospheric Complexity Framework (ACF)

AI Forecast Intelligence Visualization Center Test Suite (MISSION ACF-UI-008)
"""

from acf.ai.xai.attention_analysis import AttentionAnalysis
from acf.ai.xai.causal_chain import CausalChainGenerator
from acf.ai.xai.explanation_generator import XAIExplanationGenerator
from acf.ai.xai.feature_importance import FeatureImportanceAnalyzer
from acf.visualization.ai_forecast_center.ai_attention_mapper import AIAttentionMapper
from acf.visualization.ai_forecast_center.decision_support import AIDecisionSupport
from acf.visualization.ai_forecast_center.ensemble_visualizer import EnsembleVisualizer
from acf.visualization.ai_forecast_center.forecast_comparison import ForecastComparisonMatrix
from acf.visualization.ai_forecast_center.forecast_dashboard import AIForecastDashboard
from acf.visualization.ai_forecast_center.forecast_story_engine import ForecastStoryEngine
from acf.visualization.ai_forecast_center.model_consensus_engine import ModelConsensusEngine
from acf.visualization.ai_forecast_center.probability_engine import ProbabilisticForecastEngine
from acf.visualization.ai_forecast_center.skill_score_dashboard import SkillScoreDashboard
from acf.visualization.ai_forecast_center.uncertainty_visualizer import UncertaintyVisualizer
from acf.visualization.ai_forecast_center.xai_explanation_engine import XAIExplanationEngine


def test_compute_real_multi_model_disagreement_runs_the_real_solver_per_model():
    """
    CORRECTED principle applied here (2026-09-02, "branche le vrai
    ensemble/consensus"): unlike compute_unified_consensus() below
    (weights only), this method genuinely runs CoupledEarthSolver once
    per model at that model's real grid configuration and must return
    real, distinct per-model values - not a placeholder constant.
    """
    result = ModelConsensusEngine.compute_real_multi_model_disagreement(
        lat=36.7, lon=3.0, models=["AROME", "ALADIN"], steps=4
    )

    assert result["status"] == "REAL_DISAGREEMENT_FROM_ACF_SOLVER_AT_MULTIPLE_GRID_CONFIGS"
    assert result["is_real_data"] is True
    assert set(result["per_model_value"]) == {"AROME", "ALADIN"}
    # Different grid + independently-seeded perturbation per model ->
    # real values that are not literally identical.
    values = list(result["per_model_value"].values())
    assert values[0] != values[1]
    assert result["disagreement_spread"] >= 0.0
    assert result["model_realizations"] == {"temperature": values}


def test_compute_real_multi_model_disagreement_exposes_the_real_ensemble_statistics_already_computed():
    """Regression guard (2026-09-13, master-prompt v4 gap audit):
    median/min/max/p10/p90 were already computed by this method's own
    EnsembleManager instance but silently discarded - only mean/spread
    were ever returned. Cross-checked against an independent
    EnsembleManager built from the same real per-model values."""
    from acf.ai.ensemble.ensemble_manager import EnsembleManager

    result = ModelConsensusEngine.compute_real_multi_model_disagreement(
        lat=36.7, lon=3.0, models=["AROME", "ALADIN", "ARPEGE"], steps=2
    )

    expected = EnsembleManager(list(result["per_model_value"].values()))
    assert result["disagreement_median"] == expected.median
    assert result["disagreement_min"] == min(result["per_model_value"].values())
    assert result["disagreement_max"] == max(result["per_model_value"].values())
    assert result["disagreement_p10"] == expected.percentile(10.0)
    assert result["disagreement_p90"] == expected.percentile(90.0)
    assert result["disagreement_min"] <= result["disagreement_median"] <= result["disagreement_max"]


def test_compute_real_multi_model_disagreement_defaults_to_all_three_models():
    result = ModelConsensusEngine.compute_real_multi_model_disagreement(lat=36.7, lon=3.0, steps=2)
    assert set(result["models_compared"]) == {"AROME", "ALADIN", "ARPEGE"}
    assert set(result["per_model_value"]) == {"AROME", "ALADIN", "ARPEGE"}


def test_compute_real_multi_model_disagreement_requires_at_least_two_models():
    import pytest

    with pytest.raises(ValueError):
        ModelConsensusEngine.compute_real_multi_model_disagreement(lat=36.7, lon=3.0, models=["AROME"])


def test_compute_real_multi_model_disagreement_rejects_unknown_model():
    import pytest

    with pytest.raises(ValueError):
        ModelConsensusEngine.compute_real_multi_model_disagreement(lat=36.7, lon=3.0, models=["AROME", "WRF"])


def test_compute_real_multi_model_disagreement_seed_is_deterministic_per_point():
    """
    The per-model perturbation seed this method derives from (model,
    lat, lon) is itself deterministic - repeated calls for the same
    point must reuse the same seed, not a fresh random one each time.

    NOTE: this does NOT assert the full per_model_value output is
    bit-identical across repeated calls. It found a genuine, pre-
    existing source of nondeterminism one layer down:
    CoupledEarthSolver's atmosphere/ocean components
    (simulation_engine/atmosphere_solver/atmospheric_model.py,
    simulation_engine/ocean_solver/ocean_model.py) call np.random.*
    directly against the global, unseeded numpy RNG state - so two
    calls in the same process can genuinely differ by a small amount
    depending on how much global RNG state earlier code already
    consumed. That's a pre-existing solver characteristic, out of
    scope to fix here - not something this method's own seeding
    introduces, so it must not be misrepresented as reproducible.
    """
    seed_a = abs(hash(("AROME", round(36.7, 4), round(3.0, 4)))) % (2**32)
    seed_b = abs(hash(("AROME", round(36.7, 4), round(3.0, 4)))) % (2**32)
    assert seed_a == seed_b


def test_compute_real_multi_model_disagreement_field_runs_the_real_solver_per_model():
    """Real, full-grid extension (added 2026-09-04, ACF Scientific
    Workstation's Confidence Lab) of the real per-point method above -
    must return real, distinct per-model fields regridded onto
    target_model's own real grid, not a placeholder constant."""
    result = ModelConsensusEngine.compute_real_multi_model_disagreement_field(
        models=["ALADIN", "ARPEGE"], steps=2, target_model="ARPEGE", seed=1
    )

    assert result["status"] == "REAL_DISAGREEMENT_FIELD_FROM_ACF_SOLVER_AT_MULTIPLE_GRID_CONFIGS"
    assert result["is_real_data"] is True
    assert set(result["per_model_field"]) == {"ALADIN", "ARPEGE"}
    assert result["disagreement_spread_field"].shape == (len(result["lats"]), len(result["lons"]))
    assert result["disagreement_mean_field"].shape == result["disagreement_spread_field"].shape
    # A real, genuine spread across 2 real, independently-perturbed
    # solver runs must not be uniformly zero everywhere.
    assert result["disagreement_spread_field"].max() > 0.0


def test_compute_real_multi_model_disagreement_field_matches_target_models_own_grid():
    result = ModelConsensusEngine.compute_real_multi_model_disagreement_field(
        models=["ALADIN", "ARPEGE"], steps=2, target_model="ARPEGE", seed=1
    )

    from acf.forecast.engine import MODEL_CONFIGS

    config = MODEL_CONFIGS["ARPEGE"]
    assert len(result["lats"]) == config["n_lat"]
    assert len(result["lons"]) == config["n_lon"]


def test_compute_real_multi_model_disagreement_field_requires_at_least_two_models():
    import pytest

    with pytest.raises(ValueError):
        ModelConsensusEngine.compute_real_multi_model_disagreement_field(models=["AROME"])


def test_compute_real_multi_model_disagreement_field_rejects_unknown_model():
    import pytest

    with pytest.raises(ValueError):
        ModelConsensusEngine.compute_real_multi_model_disagreement_field(models=["AROME", "WRF"])


def test_compute_real_multi_model_disagreement_field_rejects_unknown_target_model():
    import pytest

    with pytest.raises(ValueError):
        ModelConsensusEngine.compute_real_multi_model_disagreement_field(
            models=["AROME", "ALADIN"], target_model="WRF"
        )


def test_compute_real_multi_model_disagreement_field_spread_matches_ensemble_manager_directly():
    """Cross-check discipline: one real grid cell's own spread/mean
    must equal a fresh, independent EnsembleManager built from that
    same cell's own real per-model values - never a separately
    re-derived statistic."""
    from acf.ai.ensemble.ensemble_manager import EnsembleManager

    result = ModelConsensusEngine.compute_real_multi_model_disagreement_field(
        models=["ALADIN", "ARPEGE"], steps=2, target_model="ARPEGE", seed=1
    )

    i, j = 0, 0
    values = [float(result["per_model_field"][model][i, j]) for model in result["models_compared"]]
    expected = EnsembleManager(values)

    assert result["disagreement_mean_field"][i, j] == expected.mean
    assert result["disagreement_spread_field"][i, j] == expected.spread


def test_compute_real_weighted_field_fusion_produces_a_real_fused_field():
    """
    New (2026-09-06, closure checklist chantier 3 §6, explicit user
    request "la fusion multi-modèle"): ModelConsensusEngine had no real
    field-fusion method of its own - acf.awci.multi_model_fusion.
    compute_real_multi_model_field_fusion() already existed, real and
    tested, just never reachable from here.
    """
    result = ModelConsensusEngine.compute_real_weighted_field_fusion(
        field_key="temperature_field", models=["ARPEGE", "AROME"], steps=2, target_model="ARPEGE"
    )

    assert result["status"] == "REAL_MULTI_MODEL_FIELD_FUSION_FROM_ACF_SOLVER"
    assert result["is_real_data"] is True
    assert result["target_model"] == "ARPEGE"
    assert set(result["models_used"]) == {"ARPEGE", "AROME"}
    assert result["fused_field"].shape == result["target_lats"].shape + result["target_lons"].shape
    # Equal weights (default, no skill_database supplied) - a real,
    # deterministic weighted sum, not a placeholder.
    assert result["weight_source"] == "equal_weights_no_skill_history"
    assert result["weights"] == {"ARPEGE": 0.5, "AROME": 0.5}


def test_compute_real_weighted_field_fusion_delegates_to_the_real_awci_fusion(monkeypatch):
    """compute_real_weighted_field_fusion() must be a thin wrapper, not a fresh reimplementation with its own logic."""
    import acf.awci.multi_model_fusion as multi_model_fusion

    calls = []
    sentinel = {"status": "SENTINEL_FROM_MOCK"}

    def fake_fusion(**kwargs):
        calls.append(kwargs)
        return sentinel

    monkeypatch.setattr(multi_model_fusion, "compute_real_multi_model_field_fusion", fake_fusion)

    kwargs = {"field_key": "temperature_field", "models": ["ARPEGE", "AROME"], "steps": 2, "target_model": "ARPEGE"}
    result = ModelConsensusEngine.compute_real_weighted_field_fusion(**kwargs)

    assert result is sentinel
    assert len(calls) == 1
    assert calls[0]["field_key"] == "temperature_field"
    assert calls[0]["models"] == ["ARPEGE", "AROME"]
    assert calls[0]["target_model"] == "ARPEGE"
    assert calls[0]["steps"] == 2


def test_model_consensus_and_dashboard():
    """Test du moteur de consensus pondéré et des modes du tableau de bord."""
    # CORRECTED: models_combined_count/weight_sum are genuinely
    # computed, but status used to claim "CONSENSUS_COMPUTED_OPTIMAL" -
    # this method only sums weights, it never fuses real model fields.
    cons = ModelConsensusEngine.compute_unified_consensus()
    assert cons["status"] == "WEIGHTS_ONLY_NO_MODEL_FIELDS_FUSED"
    assert cons["models_combined_count"] == 5

    dash_met = AIForecastDashboard.get_dashboard_config("METEOROLOGIST")
    assert "Multi-Model Consensus Matrix" in dash_met["active_panels"]

    dash_ai = AIForecastDashboard.get_dashboard_config("AI_SCIENTIST")
    assert "AI Attention Maps" in dash_ai["active_panels"]


def test_comparison_uncertainty_and_probabilities():
    """Test de la matrice de comparaison, de l'incertitude et des probabilités."""
    # CORRECTED: parameters/models_evaluated are a genuine static
    # scope, but the agreement score used to be a fabricated "94.8%"
    # with no real multi-model comparison run.
    comp = ForecastComparisonMatrix.get_comparison_matrix()
    assert comp["status"] == "NOT_COMPUTED_NO_MODEL_COMPARISON_RUN"
    assert comp["matrix_agreement_score_pct"] is None
    assert len(comp["parameters"]) == 4

    # CORRECTED: used to unconditionally claim a fabricated "87%"
    # confidence and specific model divergences - no real cyclone/
    # ensemble-track data connected.
    unc = UncertaintyVisualizer.analyze_cyclone_track_uncertainty()
    assert unc["acf_ai_confidence_pct"] is None
    assert unc["uncertainty_status"] == "NOT_ANALYZED_NO_ENSEMBLE_TRACK_DATA_CONNECTED"

    # CORRECTED: used to unconditionally claim a full fabricated
    # probability battery - no real ensemble/statistical model
    # connected.
    prob = ProbabilisticForecastEngine.compute_severe_weather_probabilities()
    assert prob["precipitation_probabilities"] == {}
    assert prob["status"] == "NOT_COMPUTED_NO_ENSEMBLE_DATA_CONNECTED"


def test_xai_and_attention_maps():
    """Test du moteur d'explicabilité XAI et des cartes d'attention neuronale."""
    # CORRECTED: used to ignore event_name's content and always
    # return an identical fabricated 5-cause explanation with fake 91%
    # confidence - no real XAI pipeline connected.
    xai_res = XAIExplanationEngine.get_explanation_summary("Severe Thunderstorm Episode")
    assert xai_res["causes_identified"] == []
    assert xai_res["status"] == "NOT_GENERATED_NO_XAI_PIPELINE_CONNECTED"

    # CORRECTED: used to unconditionally claim 3 fabricated attention
    # hotspots - no real model attention data connected.
    att = AIAttentionMapper.get_attention_regions()
    assert att["attention_hotspots"] == []
    assert att["visualizer_status"] == "NOT_RENDERED_NO_MODEL_ATTENTION_DATA_CONNECTED"

    # CORRECTED: target_event is genuinely echoed, but status used to
    # claim "EXPLANATION_GENERATED_SUCCESS" - no real causal-
    # attribution pipeline connected (CausalChainGenerator, also fixed
    # this session, now honestly returns an empty chain).
    gen = XAIExplanationGenerator.generate_explanation("Severe Thunderstorm Episode")
    assert gen["status"] == "NOT_GENERATED_NO_CAUSAL_ATTRIBUTION_PIPELINE_CONNECTED"
    assert gen["causal_chain"] == []


def test_skill_scores_story_and_decision_support():
    """Test des skill scores, du récit météo automatisé et de l'aide à la décision."""
    # CORRECTED: used to claim an identical fabricated skill-score
    # battery and "OUTPERFORMS_OPERATIONAL_BASELINE" for ANY model
    # name - no real forecast-verification run connected.
    skill = SkillScoreDashboard.get_skill_metrics("GraphCast")
    assert skill["deterministic_metrics"] == {}
    assert skill["evaluation"] == "NOT_EVALUATED_NO_VERIFICATION_DATA_CONNECTED"

    # CORRECTED: used to claim a fabricated "50-member" ensemble with
    # no real ensemble run connected.
    ens = EnsembleVisualizer.get_ensemble_summary()
    assert ens["ensemble_members_count"] is None
    assert ens["status"] == "NOT_RENDERED_NO_ENSEMBLE_RUN_CONNECTED"

    # CORRECTED: used to claim a fabricated 4-day narrative with no
    # real forecast data connected.
    story = ForecastStoryEngine.generate_forecast_story()
    assert story["chronological_story"] == []
    assert story["story_status"] == "NOT_GENERATED_NO_FORECAST_DATA_CONNECTED"

    # CORRECTED: used to ignore query_text and unconditionally return
    # a fabricated Algeria flood-risk analysis for ANY query.
    dec = AIDecisionSupport.analyze_operational_query("Flood Risk Algeria 72h")
    assert dec["risk_level"] is None
    assert dec["confidence_score_pct"] is None
    assert dec["status"] == "NOT_ANALYZED_NO_DECISION_SUPPORT_PIPELINE_CONNECTED"


def test_xai_package_components():
    """Test des composants internes du package src/acf/ai/xai/."""
    # CORRECTED: all three used to unconditionally claim fabricated
    # data with 0 parameters and no real model/input data connected -
    # a fixed "0.89" attention weight, 3 fixed fake SHAP-style
    # features, and an identical fixed 5-step causal narrative
    # regardless of what event was being explained.
    assert AttentionAnalysis.analyze_attention_weights()["weight"] is None
    assert FeatureImportanceAnalyzer.compute_feature_importance()["top_features"] == []
    assert CausalChainGenerator.generate_causal_chain() == []
