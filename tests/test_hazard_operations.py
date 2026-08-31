"""
Atmospheric Complexity Framework (ACF)

Emergency & Hazard Operations Test Suite (MISSION ACF-UI-009)

REWRITTEN: this whole test suite used to assert a cascade of
fabricated "real" emergency data (a named fictional cyclone, a fake
flood/wildfire scan, a fake evacuation plan for a specific region, a
fake "DISPATCH_SUCCESSFUL" emergency broadcast claim, a fake AI threat
analysis mentioning real places) - the exact same fake-stub pattern
found and fixed throughout this session, but concentrated in the
highest-real-world-stakes module found (emergency/disaster response).
See the corresponding source files' NOTE (correction) docstrings for
what each one used to fabricate. HazardDashboard and EarlyWarningSystem
were already genuinely real (real conditional logic on their inputs)
and are unchanged.
"""

from acf.ai.emergency_assistant.assistant_engine import AIEmergencyAssistant
from acf.hazard_operations.alert_generator import AlertGenerator
from acf.hazard_operations.communication_engine import CommunicationEngine
from acf.hazard_operations.crisis_timeline import CrisisTimelineEngine
from acf.hazard_operations.early_warning_system import EarlyWarningSystem
from acf.hazard_operations.emergency_manager import EmergencyManager
from acf.hazard_operations.evacuation_planner import EvacuationPlanner
from acf.hazard_operations.hazard_dashboard import HazardDashboard
from acf.hazard_operations.hazard_detection_engine import HazardDetectionEngine
from acf.hazard_operations.impact_model import ImpactModelEngine
from acf.hazard_operations.risk_assessment import RiskAssessmentEngine
from acf.hazard_operations.risk_visualization.hazard_overlay import HazardOverlayRenderer
from acf.hazard_operations.risk_visualization.risk_layers import RiskLayersManager
from acf.hazard_operations.risk_visualization.vulnerability_map import VulnerabilityMapBuilder
from acf.hazard_operations.situation_awareness import SituationalAwareness


def test_hazard_detection_and_impact_model():
    """Test du moteur de détection multi-dangers et de modélisation d'impact humain."""
    haz = HazardDetectionEngine.detect_all_hazards()
    assert haz["status"] == "NOT_SCANNED_NO_LIVE_DATA_SOURCE_CONNECTED"
    assert haz["cyclones"] == []
    assert haz["is_real_data"] is False

    impact = ImpactModelEngine.evaluate_impact("Flood Warning")
    assert impact["status"] == "NOT_EVALUATED"
    assert impact["population_exposed_count"] is None

    risk = RiskAssessmentEngine.assess_risk("Cyclone")
    assert risk["risk_score"] is None
    assert risk["is_real_data"] is False


def test_early_warning_and_evacuation_planner():
    """Test du système d'alerte précoce (GREEN/YELLOW/ORANGE/RED, réel) et du planificateur d'évacuation (non implémenté)."""
    # EarlyWarningSystem is genuinely real - unchanged.
    ews_red = EarlyWarningSystem.get_warning_level(0.85)
    assert "RED" in ews_red["warning_level"]

    ews_green = EarlyWarningSystem.get_warning_level(0.15)
    assert "GREEN" in ews_green["warning_level"]

    plan = EvacuationPlanner.plan_evacuation("Coastal Bay Area")
    assert plan["status"] == "NOT_COMPUTED_NO_SHELTER_ROUTE_DATABASE_CONNECTED"
    assert plan["total_shelter_capacity"] is None
    assert plan["safe_zones"] == []


def test_emergency_management_and_alerts():
    """Test de la gestion de crise, génération de bulletins et communication multi-canal."""
    status = EmergencyManager.get_emergency_status()
    assert status["emergency_state"] == "UNKNOWN_NO_CRISIS_TRACKING_CONNECTED"

    bulletin = AlertGenerator.generate_alert_bulletin("Severe Thunderstorm")
    assert bulletin["severity"] == "NOT_ASSESSED_SEVERITY_INPUT_REQUIRED"
    assert "SEVERE THUNDERSTORM" in bulletin["bulletin_title"]  # real: uses its own input

    comm = CommunicationEngine.dispatch_emergency_message("Severe Flood Warning")
    assert comm["dispatch_status"] == "NOT_DISPATCHED_NO_CHANNEL_INTEGRATION_CONFIGURED"
    assert comm["channels_dispatched"] == []
    assert len(comm["channels_not_configured"]) == 4

    cop = SituationalAwareness.get_cop_summary()
    assert cop["status"] == "NOT_READY_NO_DATA_SOURCE"


def test_hazard_dashboard_and_timeline():
    """Test des profils du tableau de bord (réel) et de la chronologie de crise (non implémentée)."""
    # HazardDashboard is genuinely real (branches on profile_name) - unchanged.
    dash_cp = HazardDashboard.get_dashboard_profile("CIVIL_PROTECTION")
    assert "Active Emergency Alerts" in dash_cp["active_modules"]

    dash_gov = HazardDashboard.get_dashboard_profile("GOVERNMENT_DECISION")
    assert "Global Risk Index" in dash_gov["active_modules"]

    timeline = CrisisTimelineEngine.get_crisis_timeline()
    assert timeline["status"] == "NOT_ACTIVE_NO_CRISIS_TRACKED"
    assert timeline["timeline_steps"] == []


def test_risk_visualization_components():
    """Test des composants de visualisation des risques et de vulnérabilité."""
    # RiskLayersManager is a legitimate static catalog of layer names/categories - unchanged.
    rl = RiskLayersManager.get_risk_layers()
    assert len(rl["risk_categories"]) == 4

    ho = HazardOverlayRenderer.render_hazard_overlays()
    assert ho["status"] == "NOT_RENDERED_NO_HAZARD_DATA"
    assert ho["overlays_rendered_count"] == 0

    vm = VulnerabilityMapBuilder.build_vulnerability_map()
    assert vm["status"] == "NOT_BUILT_NO_SOCIOECONOMIC_DATA_CONNECTED"


def test_ai_emergency_assistant():
    """Test de l'assistant IA pour l'analyse des menaces naturelles."""
    # CORRECTED: used to fabricate a specific "Medicane" threat
    # analysis (mentioning real places: Tunisia/Algeria/Sicily) with a
    # fake 89% confidence, regardless of the actual query text.
    ai_res = AIEmergencyAssistant.analyze_threat_query("Analyse la menace cyclonique actuelle en Méditerranée")
    assert ai_res["status"] == "NOT_ANALYZED_NO_THREAT_ANALYSIS_PIPELINE_CONNECTED"
    assert ai_res["cyclone_probability"] is None
    assert ai_res["recommended_actions"] == []
