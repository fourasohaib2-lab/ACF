"""
Atmospheric Complexity Framework (ACF)

Global Interstellar Master Framework Test Suite (MISSION ACF-041)
"""

from acf.master.awci_master_dashboard import MasterDashboard
from acf.master.capabilities import ScientificCapabilityRegistry
from acf.master.documentation_index import DocumentationIndexer
from acf.master.equation_validator import EquationValidator
from acf.master.health_monitor import HealthMonitor, HealthReport
from acf.master.master_engine import ACFMasterEngine
from acf.master.master_graph import MasterKnowledgeGraph
from acf.master.master_report import MasterExecutiveReport
from acf.master.master_settings import MasterSettings
from acf.master.module_registry import GlobalModuleRegistry
from acf.master.performance import PerformanceProfiler
from acf.master.science_gateway import MasterScienceGateway
from acf.master.scientific_certification import CertificationReport, ScientificCertificationEngine
from acf.master.traceability import EquationTrace
from acf.master.workflow_master import MasterWorkflowEngine
from acf.science.query_engine import ScientificQueryEngine


def test_acf_master_engine_lifecycle():
    """Test du cycle de vie complet d'ACFMasterEngine (discover, load, initialize, execute, shutdown)."""
    engine = ACFMasterEngine()
    modules = engine.discover_modules()
    assert len(modules) == 21

    load_res = engine.load_everything()
    assert load_res["status"] == "ALL_MODULES_LOADED"

    init_res = engine.initialize()
    assert init_res["status"] == "INITIALIZED"

    exec_res = engine.execute("Global Earth System Forecast & Defense")
    assert exec_res["execution_status"] == "SUCCESS"

    shutdown_res = engine.shutdown()
    assert shutdown_res["status"] == "SHUTDOWN_COMPLETE"


def test_global_module_and_capability_registries():
    """Test du registre des 21 modules et des 13 catégories de capacités scientifiques."""
    mods = GlobalModuleRegistry.list_modules()
    assert len(mods) == 21
    assert "Atmosphere" in mods
    assert "Planetary" in mods
    assert "Geoengineering" in mods

    caps_cats = ScientificCapabilityRegistry.list_categories()
    assert len(caps_cats) >= 13
    assert "DigitalTwin" in caps_cats

    forecast_caps = ScientificCapabilityRegistry.get_capabilities("Forecast")
    assert len(forecast_caps) >= 2


def test_master_science_gateway():
    """Test de la façade unifiée MasterScienceGateway."""
    f = MasterScienceGateway.forecast("atmosphere", 240)
    assert f["status"] == "COMPLETED"

    s = MasterScienceGateway.simulate("cyclone_surge")
    assert s["status"] == "COMPLETED"

    a = MasterScienceGateway.analyze("planetary_boundaries")
    assert a["status"] == "COMPLETED"

    r = MasterScienceGateway.reason("tropical_cyclone_intensification")
    assert r["status"] == "COMPLETED"


def test_scientific_certification_and_equation_validator():
    """Test de l'audit de certification scientifique Platinum et du validateur d'équations."""
    cert = ScientificCertificationEngine.audit_framework()
    assert isinstance(cert, CertificationReport)
    assert cert.certification_level == "CERTIFIED_PLATINUM"
    assert cert.si_compliance_pct == 100.0

    # CORRECTED: validate_equation used to always report
    # is_dimensional_correct=True/VALIDATED regardless of content - a
    # fake validator. Now honestly distinguishes real well-formedness
    # checks it does perform from dimensional analysis it does not.
    val = EquationValidator.validate_equation("E = 0.5*m*v^2", {"m": "kg", "v": "m/s"}, "WMO")
    assert val["validation_status"] == "WELL_FORMED_ONLY_NOT_DIMENSIONALLY_VERIFIED"
    assert val["is_dimensional_correct"] is None  # honestly not verified, not a fake True
    assert val["is_well_formed"] is True

    val_malformed = EquationValidator.validate_equation("not an equation", {}, "WMO")
    assert val_malformed["validation_status"] == "MALFORMED"

    trace = EquationTrace(
        law_name="Vis-Viva Equation",
        latex_equation=r"v = \sqrt{G M (2/r - 1/a)}",
        origin_publication="Philosophiæ Naturalis Principia Mathematica",
        author="Isaac Newton",
        doi="10.1098/rstl.1686.0034",
        version="1.0",
        date_added="2026-08-02",
        module_path="acf.planetary.orbital_mechanics",
        associated_tests=["test_planetary_resilience_platform.py"],
    )
    assert trace.author == "Isaac Newton"


def test_master_knowledge_graph_and_workflow_engine():
    """Test du graphe de connaissances Master et du moteur de workflows."""
    graph_node = MasterKnowledgeGraph.find("cyclone")
    assert "DigitalTwin" in graph_node["connected_domains"]

    inference = MasterKnowledgeGraph.infer("space_weather_impact")
    assert inference["confidence_pct"] > 95.0

    pipeline_res = MasterWorkflowEngine.execute_master_pipeline()
    assert pipeline_res["master_pipeline_status"].startswith("SUCCESS")


def test_master_dashboard_and_executive_reporting():
    """Test du tableau de bord AWCI Master et du générateur de rapports exécutifs."""
    meta = MasterDashboard.get_dashboard_metadata()
    assert meta["workspace_name"] == "ACF MASTER FRAMEWORK UNIFIED CONTROL CENTER"

    rep = MasterExecutiveReport.generate_report("Certification", "Markdown")
    assert rep["format"] == "Markdown"
    assert "PLATINUM CERTIFIED" in rep["content"]


def test_performance_profiler_and_health_monitor():
    """Test du profilé de performance et du moniteur de santé globale."""
    prof = PerformanceProfiler.profile_framework()
    assert prof["performance_status"] == "HIGH PERFORMANCE / OPTIMAL"

    health = HealthMonitor.check_health()
    assert isinstance(health, HealthReport)
    assert health.overall_health == "100% HEALTHY"

    doc_index = DocumentationIndexer.index_framework_documentation()
    assert doc_index["index_status"] == "UP_TO_DATE"

    settings = MasterSettings()
    assert settings.active_mode == "OPERATIONAL_FULL"
    assert settings.enable_gpu is True


def test_query_engine_master_queries():
    """Test des requêtes du ScientificQueryEngine pour le Master Framework."""
    q_engine = ScientificQueryEngine()

    r1 = q_engine.ask("Show Master")
    assert r1["workspace_name"] == "ACF MASTER FRAMEWORK UNIFIED CONTROL CENTER"

    r2 = q_engine.ask("Show Science")
    assert r2["widget_type"] == "MasterScienceGatewayViewer"

    r3 = q_engine.ask("Show Earth")
    assert r3["workspace_name"] == "PLANETARY DIGITAL TWIN"
