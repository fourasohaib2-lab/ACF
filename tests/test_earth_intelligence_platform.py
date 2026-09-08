"""
Atmospheric Complexity Framework (ACF)

Global Earth Intelligence & Autonomous Scientific Reasoning Platform Test Suite (MISSION ACF-037)
"""

from acf.intelligence.agents.manager import ScientificAgentManager
from acf.intelligence.anomalies.anomaly_engine import EarthAnomalyEngine
from acf.intelligence.decision_support.decision_engine import DecisionSupportEngine
from acf.intelligence.explanations.physics_explainer import ScientificExplanationEngine
from acf.intelligence.forecast_analysis.forecast_reasoning import ForecastReasoningEngine
from acf.intelligence.hypothesis.hypothesis_engine import HypothesisEngine
from acf.intelligence.knowledge.knowledge_updater import KnowledgeEvolutionEngine
from acf.intelligence.optimization.evacuation import EmergencyOptimizationEngine
from acf.intelligence.planner.mission_planner import MissionPlanner
from acf.intelligence.reports.executive_report import AutonomousReportGenerator
from acf.intelligence.scientific_reasoning import ScientificReasoningEngine, ScientificReasoningReport
from acf.intelligence.visualization.intelligence_dashboard import EarthIntelligenceDashboard
from acf.science.query_engine import ScientificQueryEngine


def test_scientific_reasoning_engine():
    """Test du moteur de raisonnement scientifique autonome."""
    # CORRECTED: this used to completely ignore observed_params and
    # return one of two fixed reports (fixed 95.5%/91.0% confidence)
    # based only on a "cyclone"/"storm" keyword match in the
    # phenomenon string. Now genuinely checks the real sst value
    # against the classical Palmen (1948) tropical-cyclogenesis
    # threshold (SST >= 26.5 degC); confidence_pct is no longer a
    # specific fabricated percentage since no calibrated confidence
    # model exists.
    report = ScientificReasoningEngine.evaluate_phenomenon("Tropical Cyclone", {"sst": 29.5, "cape": 1800.0})
    assert isinstance(report, ScientificReasoningReport)
    assert report.confidence_pct is None
    assert "26.5" in report.logical_chain
    assert "favorable" in report.scientific_conclusion.lower()
    assert "Bernoulli Equation" in report.physical_laws_invoked

    # Regression guard: a different sst below the threshold must yield
    # a genuinely different conclusion, not the old fixed narrative.
    cold_report = ScientificReasoningEngine.evaluate_phenomenon("Tropical Cyclone", {"sst": 20.0})
    assert "not thermodynamically favored" in cold_report.scientific_conclusion


def test_multi_agent_manager():
    """Test du gestionnaire multi-agents IA scientifiques."""
    agents = ScientificAgentManager.get_registered_agents()
    assert "MeteorologyAgent" in agents
    assert "DigitalTwinCoordinatorAgent" in agents

    # CORRECTED: used to unconditionally claim "HIGH CONSENSUS REACHED"
    # among 8 agents with fabricated findings (a fake 2.8m storm
    # surge), with 0 real agent pipeline ever run.
    assessment = ScientificAgentManager.run_collaborative_agent_assessment()
    assert assessment["active_agents_count"] == 0
    assert assessment["consensus_status"] == "NOT_RUN_NO_AGENT_PIPELINE_CONNECTED"
    assert assessment["agent_findings"] == {}


def test_hypothesis_engine_and_physics_validator():
    """Test de la génération et validation d'hypothèses physiques."""
    # CORRECTED: anomaly_name used to be accepted but never referenced
    # - this unconditionally returned the exact same 2 fixed
    # hypotheses (fabricated 88.5%/92.0% probabilities, both claimed
    # "physically validated") regardless of what anomaly was actually
    # passed in. No real anomaly-detection/hypothesis-generation
    # pipeline is connected.
    hypotheses = HypothesisEngine.generate_hypotheses("Marine Heatwave")
    assert hypotheses == []


def test_forecast_reasoning_and_model_comparison():
    """Test de la comparaison autonome entre modèles NWP et d'IA (IFS, GraphCast, NeuralGCM)."""
    # CORRECTED: used to unconditionally claim "agreement_pct: 93.8"
    # and a fabricated specific synoptic scenario regardless of
    # variable - no real forecast data from any listed model is
    # compared.
    comparison = ForecastReasoningEngine.compare_models("wind_speed")
    assert len(comparison["models_evaluated"]) == 9
    assert comparison["agreement_pct"] is None
    assert comparison["is_real_data"] is False


def test_earth_anomaly_engine():
    """
    Test de la détection d'anomalies terrestres multi-domaines.

    CORRECTED: used to unconditionally return 2 fixed fabricated
    anomalies (a fake "+4.2 sigma heatwave" at 98% confidence, a fake
    X2.4 solar flare) for ANY call, with no real planetary state
    vector ever scanned.
    """
    anomalies = EarthAnomalyEngine.scan_for_anomalies()
    assert anomalies == []


def test_decision_support_and_emergency_optimization():
    """
    Test du support décisionnel et de l'optimisation des évacuations de crise.

    CORRECTED: generate_recommendations() used to unconditionally
    return a fabricated CRITICAL "Issue Coastal Evacuation Order for
    Zone B" citing a fake "3.2m storm surge"; optimize_evacuation_plan()
    used to name specific fake evacuation routes and a fixed "6.5 hour"
    clearance time regardless of population_count - both with 0 real
    risk/road-network data connected.
    """
    recs = DecisionSupportEngine.generate_recommendations()
    assert recs == []

    evac = EmergencyOptimizationEngine.optimize_evacuation_plan(population_count=100000)
    assert evac["status"] == "NOT_OPTIMIZED_NO_ROAD_NETWORK_DATA_CONNECTED"
    assert evac["estimated_clearance_time_hours"] is None
    assert evac["target_population"] == 100000  # genuinely echoed


def test_mission_planner_and_explanation_engine():
    """Test du planificateur autonome et du moteur d'explication physique."""
    # CORRECTED: used to unconditionally claim all 4 tasks were
    # "ACTIVE / RUNNING" or "ACTIVE / SCHEDULED" with no real task
    # scheduler connected. Task names/intervals are kept as a
    # documented roadmap, but status no longer falsely claims execution.
    tasks = MissionPlanner.get_active_workflows()
    assert len(tasks) >= 4
    assert tasks[0].schedule_interval_minutes > 0
    assert tasks[0].status == "NOT_SCHEDULED"

    # CORRECTED: used to unconditionally claim a fabricated "96.4%
    # transparency confidence score" regardless of forecast_id or any
    # real forecast/alert data.
    exp = ScientificExplanationEngine.explain_forecast_decision("FCST-01")
    assert exp["transparency_confidence_score"] is None
    assert exp["forecast_id"] == "FCST-01"  # genuinely echoed


def test_knowledge_evolution_and_executive_reports():
    """Test du moteur d'évolution des connaissances et générateur de rapports d'intelligence."""
    # CORRECTED: audit_knowledge_base_consistency() used to
    # unconditionally claim "450 laws validated, 120 constants
    # verified, 100% SCIENTIFICALLY CONSISTENT" citing real-sounding
    # sources (IPCC AR6, WMO-No.8...) with no actual checking - a
    # duplicate of the same false-certification pattern already fixed
    # in master/scientific_certification.py. Now uses the real
    # ScientificRegistry law count instead of a fabricated number.
    audit = KnowledgeEvolutionEngine.audit_knowledge_base_consistency()
    assert audit["consistency_status"] == "NOT_VERIFIED_NO_AUTOMATED_CONSISTENCY_CHECK"
    assert audit["total_laws_registered"] > 0

    # CORRECTED: used to unconditionally report a fabricated Category 4
    # typhoon, a fake X2.4 solar flare, and a fake Mw 6.8 earthquake
    # with a recommended "Level-3 Coastal Evacuation" for EVERY call,
    # with 0 real domain data connected.
    rep = AutonomousReportGenerator.generate_executive_intelligence_report()
    assert rep["format"] == "Markdown"
    assert "EARTH INTELLIGENCE" in rep["content"]
    assert "NO REAL DOMAIN DATA SOURCES CONNECTED" in rep["content"]
    assert "Category 4 Typhoon" not in rep["content"]


def test_intelligence_dashboard_and_query_engine():
    """Test du tableau de bord Earth Intelligence Mission Control et des requêtes d'intelligence."""
    meta = EarthIntelligenceDashboard.get_dashboard_metadata()
    assert meta["workspace_name"] == "EARTH INTELLIGENCE MISSION CONTROL"

    q_engine = ScientificQueryEngine()

    # CORRECTED: used to claim a fixed "ai_confidence_pct: 95.5" with no
    # real reasoning engine connected here.
    r1 = q_engine.ask("Explain Forecast")
    assert r1["widget_type"] == "ScientificReasoningViewer"
    assert r1["ai_confidence_pct"] is None

    r2 = q_engine.ask("Explain Decision")
    assert r2["workspace_name"] == "EARTH INTELLIGENCE MISSION CONTROL"

    r3 = q_engine.ask("Explain Risk")
    assert r3["widget_type"] == "PlanetaryKnowledgeGraphViewer"

    r4 = q_engine.ask("Show Mission Planner")
    assert r4["widget_type"] == "MissionPlannerViewer"
