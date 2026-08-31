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
    report = ScientificReasoningEngine.evaluate_phenomenon("Tropical Cyclone", {"sst": 29.5, "cape": 1800.0})
    assert isinstance(report, ScientificReasoningReport)
    assert report.confidence_pct > 90.0
    assert "Bernoulli Equation" in report.physical_laws_invoked


def test_multi_agent_manager():
    """Test du gestionnaire multi-agents IA scientifiques."""
    agents = ScientificAgentManager.get_registered_agents()
    assert "MeteorologyAgent" in agents
    assert "DigitalTwinCoordinatorAgent" in agents

    assessment = ScientificAgentManager.run_collaborative_agent_assessment()
    assert assessment["active_agents_count"] == 8
    assert "HIGH CONSENSUS" in assessment["consensus_status"]


def test_hypothesis_engine_and_physics_validator():
    """Test de la génération et validation d'hypothèses physiques."""
    hypotheses = HypothesisEngine.generate_hypotheses("Marine Heatwave")
    assert len(hypotheses) >= 2
    assert hypotheses[0].is_physically_validated is True


def test_forecast_reasoning_and_model_comparison():
    """Test de la comparaison autonome entre modèles NWP et d'IA (IFS, GraphCast, NeuralGCM)."""
    comparison = ForecastReasoningEngine.compare_models("wind_speed")
    assert len(comparison["models_evaluated"]) == 9
    assert comparison["agreement_pct"] > 90.0


def test_earth_anomaly_engine():
    """Test de la détection d'anomalies terrestres multi-domaines."""
    anomalies = EarthAnomalyEngine.scan_for_anomalies()
    assert len(anomalies) >= 2
    assert "Heatwave" in anomalies[0].anomaly_type


def test_decision_support_and_emergency_optimization():
    """Test du support décisionnel et de l'optimisation des évacuations de crise."""
    recs = DecisionSupportEngine.generate_recommendations()
    assert len(recs) >= 2
    assert recs[0].priority_level == "CRITICAL"

    evac = EmergencyOptimizationEngine.optimize_evacuation_plan(population_count=100000)
    assert evac["estimated_clearance_time_hours"] < 10.0


def test_mission_planner_and_explanation_engine():
    """Test du planificateur autonome et du moteur d'explication physique."""
    tasks = MissionPlanner.get_active_workflows()
    assert len(tasks) >= 4
    assert tasks[0].schedule_interval_minutes > 0

    exp = ScientificExplanationEngine.explain_forecast_decision("FCST-01")
    assert exp["transparency_confidence_score"] > 90.0


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

    rep = AutonomousReportGenerator.generate_executive_intelligence_report()
    assert rep["format"] == "Markdown"
    assert "EARTH INTELLIGENCE" in rep["content"]


def test_intelligence_dashboard_and_query_engine():
    """Test du tableau de bord Earth Intelligence Mission Control et des requêtes d'intelligence."""
    meta = EarthIntelligenceDashboard.get_dashboard_metadata()
    assert meta["workspace_name"] == "EARTH INTELLIGENCE MISSION CONTROL"

    q_engine = ScientificQueryEngine()

    r1 = q_engine.ask("Explain Forecast")
    assert r1["widget_type"] == "ScientificReasoningViewer"

    r2 = q_engine.ask("Explain Decision")
    assert r2["workspace_name"] == "EARTH INTELLIGENCE MISSION CONTROL"

    r3 = q_engine.ask("Explain Risk")
    assert r3["widget_type"] == "PlanetaryKnowledgeGraphViewer"

    r4 = q_engine.ask("Show Mission Planner")
    assert r4["widget_type"] == "MissionPlannerViewer"
