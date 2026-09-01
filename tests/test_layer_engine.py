"""
Atmospheric Complexity Framework (ACF)

Scientific Layer Management & Data Fusion Engine Test Suite (MISSION ACF-UI-006)
"""

from acf.validation.anomaly import AnomalyCalculator
from acf.validation.bias_analysis import BiasAnalysis
from acf.validation.rmse import RMSECalculator
from acf.validation.verification import ScientificVerificationEngine
from acf.visualization.layer_engine.fusion_engine import DataFusionEngine
from acf.visualization.layer_engine.layer_cache import LayerCacheManager
from acf.visualization.layer_engine.layer_catalog import LayerCatalog
from acf.visualization.layer_engine.layer_dependency import LayerDependencyGraph
from acf.visualization.layer_engine.layer_manager import LayerManager
from acf.visualization.layer_engine.layer_permissions import LayerPermissionEngine
from acf.visualization.layer_engine.layer_pipeline import LayerPipeline
from acf.visualization.layer_engine.layer_query import LayerSearchEngine
from acf.visualization.layer_engine.layer_registry import LayerRegistry
from acf.visualization.layer_engine.layer_renderer import LayerRenderer


def test_layer_definition_and_registry():
    """Test de la définition canonique et du registre à 15 domaines."""
    layer = LayerRegistry.get_layer("atm.temperature.850hpa")
    assert layer is not None
    assert layer.unit == "Kelvin"
    assert layer.grib2_code == "0,0,0"

    all_layers = LayerRegistry.list_all_layers()
    assert len(all_layers) >= 5

    domains = LayerCatalog.get_domains()
    assert len(domains) == 15
    assert "01 Atmosphere Dynamics" in domains
    assert "15 AI Digital Twin" in domains


def test_layer_dependency_and_data_fusion():
    """Test du graphe de dépendance physique et du moteur de fusion multi-source."""
    tree = LayerDependencyGraph.build_causal_tree("conv.cape")
    assert "thermo.theta_e" in tree["upstream_dependencies"]

    # CORRECTED: inputs_fused is a genuine static declared source
    # list, but fusion_status used to claim "FUSED_OPTIMAL_ANALYSIS"
    # with a fabricated uncertainty/confidence - no real fusion/OI/BLUE
    # analysis was ever run.
    fusion = DataFusionEngine.fuse_data_sources("surface_temperature")
    assert fusion["fusion_status"] == "NOT_FUSED_NO_REAL_INPUT_FIELDS_PROVIDED"
    assert len(fusion["inputs_fused"]) == 5


def test_layer_search_recommendation_and_pipeline():
    """Test de la recherche naturelle, des recommandations IA et des champs de différence entre modèles."""
    results = LayerSearchEngine.search("show thunderstorm potential Europe")
    assert len(results) >= 2

    recs = LayerSearchEngine.recommend_for_situation("cyclone_detected")
    assert "ocean.sst" in recs["recommended_layers"]

    # CORRECTED: mean_absolute_difference used to be a fixed 0.35 with
    # "status": "DIFFERENCE_COMPUTED" regardless of which models/
    # variable were requested, with no real gridded fields ever diffed.
    diff = LayerPipeline.compute_model_difference("IFS", "GraphCast", "t850")
    assert diff["status"] == "NOT_COMPUTED_NO_REAL_MODEL_FIELDS_CONNECTED"
    assert diff["mean_absolute_difference"] is None
    assert diff["model_a"] == "IFS"  # genuinely echoed


def test_layer_manager_stack_and_renderer():
    """Test du gestionnaire de pile active Photoshop-style et du renderer GPU."""
    lm = LayerManager()
    lm.add_to_stack("atm.temperature.850hpa")
    lm.add_to_stack("conv.cape")
    summary = lm.get_stack_summary()
    assert summary["active_layers_count"] == 2
    assert summary["top_layer"] == "conv.cape"

    # CORRECTED: remove_from_stack() used to unconditionally return True
    # even for a layer_id that was never in the stack - a caller had no
    # way to tell a genuine removal from a no-op.
    assert lm.remove_from_stack("atm.temperature.850hpa") is True
    assert lm.get_stack_summary()["active_layers_count"] == 1
    assert lm.remove_from_stack("nonexistent.layer.id") is False
    assert lm.get_stack_summary()["active_layers_count"] == 1

    # CORRECTED: rendered_layers_count/active_stack are genuinely
    # computed, but status used to claim "RENDERED_SUCCESS" via a
    # fixed "Vulkan" backend claim - no GPU backend is connected.
    render_res = LayerRenderer.render_layer_stack(["atm.temperature.850hpa", "conv.cape"])
    assert render_res["status"] == "NOT_RENDERED_NO_GPU_BACKEND_CONNECTED"
    assert render_res["rendered_layers_count"] == 2

    cache = LayerCacheManager()
    cache.put("key1", "data1")
    assert cache.get("key1") == "data1"

    assert LayerPermissionEngine.check_layer_access("conv.cape") is True


def test_scientific_validation_engine():
    """Test des modules de validation (Biais, RMSE, Anomalies et Vérification)."""
    bias = BiasAnalysis.compute_bias(285.5, 285.0)
    assert bias["bias_value"] == 0.5

    rmse = RMSECalculator.compute_rmse([2.0, 4.0], [2.0, 5.0])
    assert rmse["rmse"] > 0.0

    anom = AnomalyCalculator.compute_anomaly(300.0, 295.0)
    assert anom["anomaly"] == 5.0

    # CORRECTED: standardized_anomaly_sigma used to divide by a
    # hardcoded "1.5" with no physical basis regardless of the
    # parameter/location, always looking like a genuine z-score.
    assert anom["standardized_anomaly_sigma"] is None  # no real std dev supplied
    anom_with_sigma = AnomalyCalculator.compute_anomaly(300.0, 295.0, climatological_std_dev=2.5)
    assert anom_with_sigma["standardized_anomaly_sigma"] == 2.0

    # CORRECTED: acc_score/rmse_temperature_k/verification_status used
    # to be fixed (0.965/0.42/"EXCELLENT_SKILL_SCORE") regardless of
    # model/obs_source, with no real forecast-vs-observation
    # verification ever computed.
    verif = ScientificVerificationEngine.verify_forecast("IFS", "SYNOP")
    assert verif["acc_score"] is None
    assert verif["verification_status"] == "NOT_VERIFIED_NO_REAL_OBSERVATION_COMPARISON_CONNECTED"
    assert verif["model_evaluated"] == "IFS"  # genuinely echoed
