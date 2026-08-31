"""
Atmospheric Complexity Framework (ACF)

Global Autonomous AI Meteorologist & Earth System Expert Test Suite (MISSION ACF-043)

REWRITTEN: nearly every class in acf.ai_expert used to unconditionally return
fixed, fabricated scientific/operational claims (specific hazard states,
evacuation orders, confidence scores, model consensus summaries) regardless
of any real data, input parameter, or actual conditions - the same fake-stub
pattern found and fixed throughout this session, here in a directory that had
NOT been previously audited despite query_engine.py's own callers into a
*separate*, already-fixed implementation of similar functionality (see the
"CORRECTED" comments in test_query_engine_ai_expert_queries() below, which
predate this file's own fix and only patched query_engine.py's independent
code path - it does not import acf.ai_expert at all, verified via grep - so
these root classes remained just as dangerous for any direct caller). Two of
the fabrications here were genuinely operationally dangerous even by this
session's standards: AIDecisionSupport.generate_decision_bulletin() claimed a
fabricated "EVACUATE LOW-LYING COASTAL ZONES" order "APPROVED BY AI CHIEF
METEOROLOGIST", and RecommendationEngine.generate_sectorial_recommendations()
claimed fabricated real-world actions like "Open spillway gates at Reservoir
Beta". See each fixed module's NOTE (correction) docstring for detail.
"""

from acf.ai_expert.ai_meteorologist import AIMeteorologist
from acf.ai_expert.air_quality_reasoning import AirQualityReasoningEngine
from acf.ai_expert.aviation_reasoning import AviationReasoningEngine
from acf.ai_expert.awci_ai_dashboard import AWCI_AIDashboard
from acf.ai_expert.climate_reasoning import ClimateReasoningEngine
from acf.ai_expert.confidence_engine import ConfidenceEngine
from acf.ai_expert.convective_analysis import ConvectiveAnalyzer
from acf.ai_expert.cryosphere_reasoning import CryosphereReasoningEngine
from acf.ai_expert.decision_support import AIDecisionSupport
from acf.ai_expert.earth_system_expert import EarthSystemExpert
from acf.ai_expert.executive_briefing import ExecutiveBriefingGenerator
from acf.ai_expert.explanation_engine import ExplainableAIEngine
from acf.ai_expert.forecast_interpreter import ForecastInterpreter
from acf.ai_expert.hazard_reasoning import HazardReasoningEngine
from acf.ai_expert.hydrology_reasoning import HydrologyReasoningEngine
from acf.ai_expert.hypothesis_engine import HypothesisGenerator
from acf.ai_expert.marine_reasoning import MarineReasoningEngine
from acf.ai_expert.mesoscale_analysis import MesoscaleAnalyzer
from acf.ai_expert.ocean_reasoning import OceanReasoningEngine
from acf.ai_expert.reasoning_engine import ScientificReasoningEngine
from acf.ai_expert.recommendation_engine import RecommendationEngine
from acf.ai_expert.scientific_dialog import ScientificDialogEngine
from acf.ai_expert.space_weather_reasoning import SpaceWeatherReasoningEngine
from acf.ai_expert.synoptic_analysis import SynopticAnalyzer
from acf.ai_expert.tropical_analysis import TropicalAnalyzer
from acf.ai_expert.uncertainty_engine import UncertaintyEngine
from acf.science.query_engine import ScientificQueryEngine


def test_ai_meteorologist_and_earth_system_expert():
    """Test du Météorologiste Virtuel et de l'Expert Système Terre."""
    ai = AIMeteorologist()
    mon = ai.monitor_earth_system()
    assert mon["system_status"] == "ACTIVE / OPERATIONAL"
    # CORRECTED: active_alerts_count used to be hard-coded 0 (masking any
    # real active alert); now honestly None with no alert system connected.
    assert mon["active_alerts_count"] is None
    assert mon["alerts_status"] == "NOT_TRACKED_NO_ALERT_SYSTEM_CONNECTED"

    daily = ai.generate_daily_forecast_analysis()
    assert daily["overall_confidence_score_pct"] is None
    assert daily["is_real_data"] is False

    state = EarthSystemExpert.evaluate_global_earth_state()
    assert "atmosphere" in state
    assert "ocean" in state
    assert "hydrology" in state
    assert state["atmosphere"] is None
    assert state["is_real_data"] is False


def test_reasoning_and_forecast_interpreter():
    """Test du moteur de raisonnement physique et de l'interprète de prévision."""
    chain = ScientificReasoningEngine.deduce_causal_chain("supercell_hail")
    assert chain["reasoning_steps"] == []
    assert chain["is_real_data"] is False

    conv_interp = ForecastInterpreter.interpret_convection(cape=2000.0, cin=-20.0)
    assert "CAPE=2000.0" in conv_interp
    assert "not available" in conv_interp

    pv_interp = ForecastInterpreter.interpret_cyclone_evolution(pv_anomaly_pvus=3.5)
    assert "3.5 PVU" in pv_interp
    assert "not available" in pv_interp

    tele_interp = ForecastInterpreter.interpret_teleconnections(nao_index=1.2, enso_oni=0.8)
    assert tele_interp["synoptic_impact"] is None
    assert tele_interp["nao_index"] == 1.2


def test_specialized_domain_analyzers():
    """Test des analyseurs spécialisés (synoptique, méso-échelle, convectif, tropical)."""
    syn = SynopticAnalyzer.analyze_synoptic_chart()
    assert syn["patterns"] == []
    assert syn["is_real_data"] is False

    meso = MesoscaleAnalyzer.analyze_mesoscale_features()
    assert meso["features"] == []

    # CORRECTED: used to unconditionally claim "HIGH" severity regardless
    # of the cape/shear_0_6km values actually passed in.
    conv = ConvectiveAnalyzer.analyze_convective_environment(cape=2200.0, shear_0_6km=22.0)
    assert conv["cape_j_kg"] == 2200.0  # genuinely echoed
    assert conv["storm_severity_index"] is None

    trop = TropicalAnalyzer.analyze_tropical_system("Category 4 Cyclone")
    assert trop["system_name"] == "Category 4 Cyclone"  # genuinely echoed
    assert trop["rapid_intensification_risk"] is None


def test_multi_sphere_reasoning_engines():
    """Test des 9 moteurs de raisonnement géophysiques - tous désormais honnêtes plutôt que fabriqués."""
    climate = ClimateReasoningEngine.analyze_climate_state()
    assert climate["active_teleconnections"] == []
    assert climate["is_real_data"] is False

    ocean = OceanReasoningEngine.analyze_ocean_state()
    assert ocean["is_real_data"] is False  # fixed earlier this session

    hydro = HydrologyReasoningEngine.analyze_hydrology_state()
    assert hydro["flood_alert_level"] is None

    cryo = CryosphereReasoningEngine.analyze_cryosphere_state()
    assert cryo["sea_ice_thickness_m"] is None

    space = SpaceWeatherReasoningEngine.analyze_space_weather_state()
    assert space["kp_index"] is None

    aq = AirQualityReasoningEngine.analyze_air_quality_state()
    assert aq["pm25_ug_m3"] is None

    # CORRECTED (aviation-safety-relevant): used to unconditionally claim
    # a fixed "FL360" recommended flight level.
    avi = AviationReasoningEngine.analyze_flight_hazards()
    assert avi["recommended_flight_level"] is None

    marine = MarineReasoningEngine.analyze_marine_hazards()
    assert marine["sea_state"] is None

    # CORRECTED: used to unconditionally claim "Category 4 Tropical
    # Cyclone" / "RED / EXTREME" for any call.
    haz = HazardReasoningEngine.evaluate_cascade_risks()
    assert haz["primary_hazard"] is None
    assert haz["overall_threat_level"] is None


def test_ai_confidence_xai_and_hypotheses():
    """Test du moteur de confiance multi-modèles (10 modèles), de l'IA explicable XAI et des hypothèses."""
    conf = ConfidenceEngine.evaluate_multi_model_confidence()
    assert len(conf["models_consulted"]) == 10  # genuine static list, unchanged
    assert "GraphCast" in conf["models_consulted"]
    # CORRECTED: used to unconditionally claim "92.5%" confidence.
    assert conf["overall_confidence_pct"] is None

    unc = UncertaintyEngine.quantify_uncertainty()
    assert unc["uncertainty_level"] is None

    xai = ExplainableAIEngine.explain_recommendation("Red Warning Surge")
    assert xai["physical_laws_involved"] == []
    assert xai["observed_evidence"] is None

    hypo = HypothesisGenerator.generate_hypothesis("rapid_intensification")
    assert hypo["hypothesis"] is None
    assert hypo["event_type"] == "rapid_intensification"  # genuinely echoed


def test_recommendations_briefings_and_dashboard():
    """Test du moteur de recommandations sectorielles, des bulletins et du tableau de bord AWCI."""
    # CORRECTED (most operationally dangerous finding in this cluster):
    # used to unconditionally claim fabricated real-world operational
    # actions ("Open spillway gates at Reservoir Beta"...).
    recs = RecommendationEngine.generate_sectorial_recommendations()
    assert recs["civil_protection"] == []
    assert recs["is_real_data"] is False

    # CORRECTED (most operationally dangerous finding alongside the
    # above): used to unconditionally claim a fabricated "EVACUATE
    # LOW-LYING COASTAL ZONES" order "APPROVED BY AI CHIEF METEOROLOGIST".
    bull = AIDecisionSupport.generate_decision_bulletin()
    assert bull["priority"] is None
    assert bull["recommended_action"] is None

    dialog = ScientificDialogEngine.process_user_query("Explain jet stream")
    assert dialog["confidence_score_pct"] is None
    assert dialog["user_query"] == "Explain jet stream"  # genuinely echoed

    briefing = ExecutiveBriefingGenerator.generate_full_executive_briefing()
    assert "meteorology_briefing" in briefing
    assert briefing["meteorology_briefing"] is None
    assert briefing["is_real_data"] is False

    # AWCI dashboard metadata is genuine static UI configuration, not
    # fabricated data - unchanged.
    dash = AWCI_AIDashboard.get_dashboard_metadata()
    assert dash["workspace_name"] == "AUTONOMOUS AI METEOROLOGIST & EARTH SYSTEM EXPERT WORKSPACE"


def test_query_engine_ai_expert_queries():
    """Test des requêtes du ScientificQueryEngine pour le Météorologiste Virtuel autonome."""
    q_engine = ScientificQueryEngine()

    # NOTE: ScientificQueryEngine.ask() has its own, separate,
    # already-honestly-fixed implementation for these queries (verified:
    # query_engine.py does not import acf.ai_expert at all) - unaffected
    # by this file's fixes to the acf.ai_expert classes themselves.
    r1 = q_engine.ask("Explain today's forecast")
    assert r1["workspace_name"] == "AUTONOMOUS AI METEOROLOGIST & EARTH SYSTEM EXPERT WORKSPACE"
    assert r1["is_real_data"] is False

    r2 = q_engine.ask("Why is heavy rain expected")
    assert "PWV" in r2["physical_explanation"]

    r3 = q_engine.ask("Which model is most reliable")
    assert "GraphCast" in r3["recommended_best_model"]

    r4 = q_engine.ask("Show uncertainty")
    assert r4["widget_type"] == "UncertaintyQuantificationViewer"
    assert r4["uncertainty_level"] is None

    r5 = q_engine.ask("Recommend emergency actions")
    assert r5["widget_type"] == "SectorialRecommendationViewer"
    assert r5["priority"] is None

    r6 = q_engine.ask("Generate operational briefing")
    assert r6["report_type"] == "Executive Briefing"
