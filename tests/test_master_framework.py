"""
Atmospheric Complexity Framework (ACF)

Global Interstellar Master Framework Test Suite (MISSION ACF-041)
"""

import pytest

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

    # CORRECTED: execute() genuinely echoed task_name, but used to
    # unconditionally claim "SUCCESS" and a fixed 5-subsystem
    # orchestration list - no real subsystem call is wired up (see
    # master_engine.py's NOTE: acf.simulation_engine has no API yet,
    # and the reasoning engine it would coordinate is itself not fully
    # real).
    exec_res = engine.execute("Global Earth System Forecast & Defense")
    assert exec_res["execution_status"] == "NOT_EXECUTED_NO_SUBSYSTEM_ORCHESTRATION_WIRED"
    assert exec_res["orchestrated_subsystems"] == []

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
    # CORRECTED: all 8 gateway methods used to echo their own input
    # and unconditionally claim "COMPLETED"/"ANSWERED"/"RENDERED" with
    # no real dispatch into any underlying subsystem - investigated
    # this session (see science_gateway.py's class-level NOTE):
    # acf.simulation_engine has no callable API at all yet, and the
    # reasoning engine a real .reason() would delegate to itself
    # ignores its own observed_params argument.
    f = MasterScienceGateway.forecast("atmosphere", 240)
    assert f["status"] == "NOT_DISPATCHED_NO_FORECAST_ENGINE_WIRED"
    assert f["domain"] == "atmosphere"

    s = MasterScienceGateway.simulate("cyclone_surge")
    assert s["status"] == "NOT_DISPATCHED_NO_SIMULATION_ENGINE_WIRED"

    a = MasterScienceGateway.analyze("planetary_boundaries")
    assert a["status"] == "NOT_DISPATCHED_NO_ANALYSIS_ENGINE_WIRED"

    r = MasterScienceGateway.reason("tropical_cyclone_intensification")
    assert r["status"] == "NOT_DISPATCHED_NO_REASONING_ENGINE_WIRED"


def test_scientific_certification_and_equation_validator():
    """Test de l'audit de certification scientifique Platinum et du validateur d'équations."""
    # CORRECTED: audit_framework() used to unconditionally claim
    # "CERTIFIED_PLATINUM" / 100% SI compliance / 450 equations audited
    # with zero actual verification performed - the single most
    # consequential fake-stub finding of this session (a framework
    # falsely self-certifying as fully verified). Now honestly reports
    # no real audit was performed.
    cert = ScientificCertificationEngine.audit_framework()
    assert isinstance(cert, CertificationReport)
    assert cert.certification_level == "NOT_AUDITED"
    assert cert.si_compliance_pct == 0.0
    assert cert.equations_audited_count == 0

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
    # CORRECTED: find()/infer() used to return fixed fake data for ANY
    # input (find("cyclone") and find(anything) gave identical fake
    # domains; infer() always returned the same fabricated causal
    # chain and a fake 98.5% confidence). find() now genuinely queries
    # EncyclopediaRegistry - a real search for "cyclone" turns up real
    # matching domains (Dynamique Atmospherique, Ocean-Atmosphere,
    # Phenomenes Violents & Grele, etc.), not the old fake
    # ["Atmosphere","Ocean","Hydrology","DigitalTwin"].
    graph_node = MasterKnowledgeGraph.find("cyclone")
    assert graph_node["is_real_data"] is True
    assert graph_node["relationships_count"] > 0
    assert "Océan-Atmosphère" in graph_node["connected_domains"]

    # infer() has no real causal-reasoning engine behind it - honestly
    # raises instead of fabricating a causal chain and fake confidence.
    with pytest.raises(NotImplementedError):
        MasterKnowledgeGraph.infer("space_weather_impact")

    # CORRECTED: execute_master_pipeline() used to unconditionally
    # claim "SUCCESS / ALL PIPELINES COMPLETED" while running none of
    # its 8 named stages - same false-success pattern as EarthSolver.
    # Now honestly reports nothing actually ran.
    pipeline_res = MasterWorkflowEngine.execute_master_pipeline()
    assert pipeline_res["master_pipeline_status"] == "NOT_EXECUTED_PLACEHOLDER_ONLY"
    assert pipeline_res["pipelines_executed"] == []
    assert len(pipeline_res["pipelines_defined_but_not_run"]) == 8


def test_master_dashboard_and_executive_reporting():
    """Test du tableau de bord AWCI Master et du générateur de rapports exécutifs."""
    meta = MasterDashboard.get_dashboard_metadata()
    assert meta["workspace_name"] == "ACF MASTER FRAMEWORK UNIFIED CONTROL CENTER"

    # CORRECTED: generate_report() used to hard-code "PLATINUM
    # CERTIFIED (100% SI & WMO/NOAA/NASA Compliance)" and "2006+
    # Passed" tests into the report text regardless of the framework's
    # actual state - the same false claim already fixed in
    # ScientificCertificationEngine. Now pulls the real (honest,
    # NOT_AUDITED) certification result instead.
    rep = MasterExecutiveReport.generate_report("Certification", "Markdown")
    assert rep["format"] == "Markdown"
    assert "NOT_AUDITED" in rep["content"]
    assert "PLATINUM CERTIFIED" not in rep["content"]


def test_performance_profiler_and_health_monitor():
    """Test du profilé de performance et du moniteur de santé globale."""
    # CORRECTED: profile_framework() used to return fixed fake
    # telemetry ("HIGH PERFORMANCE / OPTIMAL" always) - now reports
    # real psutil-measured CPU/RAM (or honestly reports psutil is
    # absent), so the exact status can legitimately vary with real
    # system load. Check the real, meaningful invariants instead.
    prof = PerformanceProfiler.profile_framework()
    assert prof["performance_status"] in ("NORMAL", "ELEVATED", "HIGH_LOAD", "UNKNOWN_PSUTIL_NOT_INSTALLED")
    if prof["is_real_data"]:
        assert 0.0 <= prof["cpu_utilization_pct"] <= 100.0
        assert prof["ram_used_gb"] > 0

    # CORRECTED: check_health() used to unconditionally report "100%
    # HEALTHY" for all 7 subsystems regardless of their actual state -
    # now genuinely imports each subsystem's package and reports real
    # per-subsystem status.
    health = HealthMonitor.check_health()
    assert isinstance(health, HealthReport)
    assert "HEALTHY" in health.overall_health
    assert all(
        status.startswith("HEALTHY") or status.startswith("FAILED") for status in health.subsystem_statuses.values()
    )

    # CORRECTED: index_framework_documentation() used to return fixed
    # fake counts (350/1200/450/850, "UP_TO_DATE") regardless of the
    # codebase's actual content. Now performs a real AST scan + real
    # registry queries.
    doc_index = DocumentationIndexer.index_framework_documentation()
    assert doc_index["index_status"] == "INDEXED_FROM_LIVE_SCAN"
    assert doc_index["is_real_data"] is True
    assert doc_index["total_classes_indexed"] > 100  # real codebase has hundreds of classes
    assert doc_index["total_functions_indexed"] > 100
    assert doc_index["total_laws_indexed"] > 0

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
