"""
Atmospheric Complexity Framework (ACF)

Scientific Layer Management & Data Fusion Engine Test Suite (MISSION ACF-UI-006)
"""

from acf.visualization.layer_engine.layer_metadata import LayerDefinition
from acf.visualization.layer_engine.layer_registry import LayerRegistry
from acf.visualization.layer_engine.layer_catalog import LayerCatalog
from acf.visualization.layer_engine.layer_dependency import LayerDependencyGraph
from acf.visualization.layer_engine.fusion_engine import DataFusionEngine
from acf.visualization.layer_engine.layer_query import LayerSearchEngine
from acf.visualization.layer_engine.layer_cache import LayerCacheManager
from acf.visualization.layer_engine.layer_permissions import LayerPermissionEngine
from acf.visualization.layer_engine.layer_renderer import LayerRenderer
from acf.visualization.layer_engine.layer_pipeline import LayerPipeline
from acf.visualization.layer_engine.layer_manager import LayerManager
from acf.validation.bias_analysis import BiasAnalysis
from acf.validation.rmse import RMSECalculator
from acf.validation.anomaly import AnomalyCalculator
from acf.validation.verification import ScientificVerificationEngine


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

    fusion = DataFusionEngine.fuse_data_sources("surface_temperature")
    assert fusion["fusion_status"] == "FUSED_OPTIMAL_ANALYSIS"
    assert len(fusion["inputs_fused"]) == 5


def test_layer_search_recommendation_and_pipeline():
    """Test de la recherche naturelle, des recommandations IA et des champs de différence entre modèles."""
    results = LayerSearchEngine.search("show thunderstorm potential Europe")
    assert len(results) >= 2

    recs = LayerSearchEngine.recommend_for_situation("cyclone_detected")
    assert "ocean.sst" in recs["recommended_layers"]

    diff = LayerPipeline.compute_model_difference("IFS", "GraphCast", "t850")
    assert diff["status"] == "DIFFERENCE_COMPUTED"
    assert diff["model_a"] == "IFS"


def test_layer_manager_stack_and_renderer():
    """Test du gestionnaire de pile active Photoshop-style et du renderer GPU."""
    lm = LayerManager()
    lm.add_to_stack("atm.temperature.850hpa")
    lm.add_to_stack("conv.cape")
    summary = lm.get_stack_summary()
    assert summary["active_layers_count"] == 2
    assert summary["top_layer"] == "conv.cape"

    render_res = LayerRenderer.render_layer_stack(["atm.temperature.850hpa", "conv.cape"])
    assert render_res["status"] == "RENDERED_SUCCESS"

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

    verif = ScientificVerificationEngine.verify_forecast("IFS", "SYNOP")
    assert verif["acc_score"] > 0.9
