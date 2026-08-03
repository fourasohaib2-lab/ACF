"""
Atmospheric Complexity Framework (ACF)

Emergency & Hazard Operations Test Suite (MISSION ACF-UI-009)
"""

from acf.hazard_operations.hazard_dashboard import HazardDashboard
from acf.hazard_operations.hazard_detection_engine import HazardDetectionEngine
from acf.hazard_operations.risk_assessment import RiskAssessmentEngine
from acf.hazard_operations.early_warning_system import EarlyWarningSystem
from acf.hazard_operations.impact_model import ImpactModelEngine
from acf.hazard_operations.emergency_manager import EmergencyManager
from acf.hazard_operations.alert_generator import AlertGenerator
from acf.hazard_operations.communication_engine import CommunicationEngine
from acf.hazard_operations.evacuation_planner import EvacuationPlanner
from acf.hazard_operations.crisis_timeline import CrisisTimelineEngine
from acf.hazard_operations.situation_awareness import SituationalAwareness
from acf.hazard_operations.risk_visualization.risk_layers import RiskLayersManager
from acf.hazard_operations.risk_visualization.hazard_overlay import HazardOverlayRenderer
from acf.hazard_operations.risk_visualization.vulnerability_map import VulnerabilityMapBuilder
from acf.ai.emergency_assistant.assistant_engine import AIEmergencyAssistant


def test_hazard_detection_and_impact_model():
    """Test du moteur de détection multi-dangers et de modélisation d'impact humain."""
    haz = HazardDetectionEngine.detect_all_hazards()
    assert haz["status"] == "DETECTION_SCAN_COMPLETED"
    assert len(haz["cyclones"]) >= 1
    assert haz["cyclones"][0]["category"] == 3

    impact = ImpactModelEngine.evaluate_impact("Flood Warning")
    assert impact["status"] == "IMPACT_EVALUATED"
    assert impact["overall_impact_level"] == "CRITICAL"
    assert impact["population_exposed_count"] == 240000


def test_early_warning_and_evacuation_planner():
    """Test du système d'alerte précoce (GREEN/YELLOW/ORANGE/RED) et du planificateur d'évacuation."""
    ews_red = EarlyWarningSystem.get_warning_level(0.85)
    assert "RED" in ews_red["warning_level"]

    ews_green = EarlyWarningSystem.get_warning_level(0.15)
    assert "GREEN" in ews_green["warning_level"]

    plan = EvacuationPlanner.plan_evacuation("Coastal Bay Area")
    assert plan["status"] == "PLAN_COMPUTED"
    assert plan["total_shelter_capacity"] == 350000
    assert len(plan["safe_zones"]) >= 2


def test_emergency_management_and_alerts():
    """Test de la gestion de crise, génération de bulletins et communication multi-canal."""
    status = EmergencyManager.get_emergency_status()
    assert status["emergency_state"] == "ACTIVE_RED_ALERT"

    bulletin = AlertGenerator.generate_alert_bulletin("Severe Thunderstorm")
    assert bulletin["severity"] == "RED_ALERT"

    comm = CommunicationEngine.dispatch_emergency_message("Severe Flood Warning")
    assert comm["dispatch_status"] == "DISPATCH_SUCCESSFUL"
    assert len(comm["channels_dispatched"]) == 4

    cop = SituationalAwareness.get_cop_summary()
    assert cop["status"] == "COP_READY"


def test_hazard_dashboard_and_timeline():
    """Test des profils du tableau de bord et de la chronologie de crise."""
    dash_cp = HazardDashboard.get_dashboard_profile("CIVIL_PROTECTION")
    assert "Active Emergency Alerts" in dash_cp["active_modules"]

    dash_gov = HazardDashboard.get_dashboard_profile("GOVERNMENT_DECISION")
    assert "Global Risk Index" in dash_gov["active_modules"]

    timeline = CrisisTimelineEngine.get_crisis_timeline()
    assert timeline["status"] == "TIMELINE_ACTIVE"
    assert len(timeline["timeline_steps"]) == 5


def test_risk_visualization_components():
    """Test des composants de visualisation des risques et de vulnérabilité."""
    rl = RiskLayersManager.get_risk_layers()
    assert len(rl["risk_categories"]) == 4

    ho = HazardOverlayRenderer.render_hazard_overlays()
    assert ho["status"] == "OVERLAYS_RENDERED"

    vm = VulnerabilityMapBuilder.build_vulnerability_map()
    assert vm["status"] == "VULNERABILITY_MAP_BUILT"


def test_ai_emergency_assistant():
    """Test de l'assistant IA pour l'analyse des menaces naturelles."""
    ai_res = AIEmergencyAssistant.analyze_threat_query("Analyse la menace cyclonique actuelle en Méditerranée")
    assert ai_res["status"] == "THREAT_ANALYSIS_COMPLETE"
    assert ai_res["cyclone_probability"] == 0.74
    assert len(ai_res["recommended_actions"]) >= 3
