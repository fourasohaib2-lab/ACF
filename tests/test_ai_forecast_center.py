"""
Atmospheric Complexity Framework (ACF)

AI Forecast Intelligence Visualization Center Test Suite (MISSION ACF-UI-008)
"""

from acf.visualization.ai_forecast_center.forecast_dashboard import AIForecastDashboard
from acf.visualization.ai_forecast_center.model_consensus_engine import ModelConsensusEngine
from acf.visualization.ai_forecast_center.forecast_comparison import ForecastComparisonMatrix
from acf.visualization.ai_forecast_center.uncertainty_visualizer import UncertaintyVisualizer
from acf.visualization.ai_forecast_center.probability_engine import ProbabilisticForecastEngine
from acf.visualization.ai_forecast_center.xai_explanation_engine import XAIExplanationEngine
from acf.visualization.ai_forecast_center.ai_attention_mapper import AIAttentionMapper
from acf.visualization.ai_forecast_center.skill_score_dashboard import SkillScoreDashboard
from acf.visualization.ai_forecast_center.ensemble_visualizer import EnsembleVisualizer
from acf.visualization.ai_forecast_center.forecast_story_engine import ForecastStoryEngine
from acf.visualization.ai_forecast_center.decision_support import AIDecisionSupport
from acf.ai.xai.attention_analysis import AttentionAnalysis
from acf.ai.xai.feature_importance import FeatureImportanceAnalyzer
from acf.ai.xai.causal_chain import CausalChainGenerator
from acf.ai.xai.explanation_generator import XAIExplanationGenerator


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
    comp = ForecastComparisonMatrix.get_comparison_matrix()
    assert comp["status"] == "COMPARISON_MATRIX_READY"

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

    att = AIAttentionMapper.get_attention_regions()
    assert len(att["attention_hotspots"]) == 3

    gen = XAIExplanationGenerator.generate_explanation("Severe Thunderstorm Episode")
    assert gen["status"] == "EXPLANATION_GENERATED_SUCCESS"


def test_skill_scores_story_and_decision_support():
    """Test des skill scores, du récit météo automatisé et de l'aide à la décision."""
    skill = SkillScoreDashboard.get_skill_metrics("GraphCast")
    assert skill["deterministic_metrics"]["ACC_Z500"] == 0.978

    ens = EnsembleVisualizer.get_ensemble_summary()
    assert ens["ensemble_members_count"] == 50

    story = ForecastStoryEngine.generate_forecast_story()
    assert len(story["chronological_story"]) == 4

    dec = AIDecisionSupport.analyze_operational_query("Flood Risk Algeria 72h")
    assert dec["risk_level"] == "HIGH"
    assert dec["confidence_score_pct"] == 78.0


def test_xai_package_components():
    """Test des composants internes du package src/acf/ai/xai/."""
    assert AttentionAnalysis.analyze_attention_weights()["weight"] > 0.8
    assert len(FeatureImportanceAnalyzer.compute_feature_importance()["top_features"]) == 3
    assert len(CausalChainGenerator.generate_causal_chain()) == 5
