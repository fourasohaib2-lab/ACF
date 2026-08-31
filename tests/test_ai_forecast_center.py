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


def test_model_consensus_and_dashboard():
    """Test du moteur de consensus pondéré et des modes du tableau de bord."""
    cons = ModelConsensusEngine.compute_unified_consensus()
    assert cons["status"] == "CONSENSUS_COMPUTED_OPTIMAL"
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

    unc = UncertaintyVisualizer.analyze_cyclone_track_uncertainty()
    assert unc["acf_ai_confidence_pct"] == 87.0

    prob = ProbabilisticForecastEngine.compute_severe_weather_probabilities()
    assert prob["precipitation_probabilities"]["P(RR > 10mm)"] == 0.95
    assert prob["thunderstorm_probabilities"]["P(Supercell)"] == 0.52


def test_xai_and_attention_maps():
    """Test du moteur d'explicabilité XAI et des cartes d'attention neuronale."""
    xai_res = XAIExplanationEngine.get_explanation_summary("Severe Thunderstorm Episode")
    assert len(xai_res["causes_identified"]) == 5
    assert xai_res["ai_confidence_pct"] == 91.0

    # CORRECTED: used to unconditionally claim 3 fabricated attention
    # hotspots - no real model attention data connected.
    att = AIAttentionMapper.get_attention_regions()
    assert att["attention_hotspots"] == []
    assert att["visualizer_status"] == "NOT_RENDERED_NO_MODEL_ATTENTION_DATA_CONNECTED"

    gen = XAIExplanationGenerator.generate_explanation("Severe Thunderstorm Episode")
    assert gen["status"] == "EXPLANATION_GENERATED_SUCCESS"


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
    assert AttentionAnalysis.analyze_attention_weights()["weight"] > 0.8
    assert len(FeatureImportanceAnalyzer.compute_feature_importance()["top_features"]) == 3
    assert len(CausalChainGenerator.generate_causal_chain()) == 5
