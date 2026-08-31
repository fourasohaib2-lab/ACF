"""
Atmospheric Complexity Framework (ACF)

Global Autonomous AI Meteorologist & Earth System Expert Test Suite (MISSION ACF-043)
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

    daily = ai.generate_daily_forecast_analysis()
    assert daily["overall_confidence_score_pct"] > 90.0

    state = EarthSystemExpert.evaluate_global_earth_state()
    assert "atmosphere" in state
    assert "ocean" in state
    assert "hydrology" in state


def test_reasoning_and_forecast_interpreter():
    """Test du moteur de raisonnement physique et de l'interprète de prévision."""
    chain = ScientificReasoningEngine.deduce_causal_chain("supercell_hail")
    assert len(chain["reasoning_steps"]) >= 4

    conv_interp = ForecastInterpreter.interpret_convection(cape=2000.0, cin=-20.0)
    assert "severe explosive convection" in conv_interp

    pv_interp = ForecastInterpreter.interpret_cyclone_evolution(pv_anomaly_pvus=3.5)
    assert "PV anomaly" in pv_interp

    tele_interp = ForecastInterpreter.interpret_teleconnections(nao_index=1.2, enso_oni=0.8)
    assert "NAO+" in tele_interp["synoptic_impact"]


def test_specialized_domain_analyzers():
    """Test des analyseurs spécialisés (synoptique, méso-échelle, convectif, tropical)."""
    syn = SynopticAnalyzer.analyze_synoptic_chart()
    assert "Icelandic Low (982 hPa)" in syn["patterns"]

    meso = MesoscaleAnalyzer.analyze_mesoscale_features()
    assert len(meso["features"]) >= 3

    conv = ConvectiveAnalyzer.analyze_convective_environment(cape=2200.0, shear_0_6km=22.0)
    assert conv["storm_severity_index"] == "HIGH"

    trop = TropicalAnalyzer.analyze_tropical_system("Category 4 Cyclone")
    assert trop["rapid_intensification_risk"] == "HIGH (SST 30°C + Low Shear 5 kt)"


def test_multi_sphere_reasoning_engines():
    """Test des 9 moteurs de raisonnement géophysiques."""
    assert "active_teleconnections" in ClimateReasoningEngine.analyze_climate_state()
    assert "sst_anomaly" in OceanReasoningEngine.analyze_ocean_state()
    assert "river_discharge_m3_s" in HydrologyReasoningEngine.analyze_hydrology_state()
    assert "sea_ice_thickness_m" in CryosphereReasoningEngine.analyze_cryosphere_state()
    assert "kp_index" in SpaceWeatherReasoningEngine.analyze_space_weather_state()
    assert "pm25_ug_m3" in AirQualityReasoningEngine.analyze_air_quality_state()
    assert "recommended_flight_level" in AviationReasoningEngine.analyze_flight_hazards()
    assert "sea_state" in MarineReasoningEngine.analyze_marine_hazards()
    assert "primary_hazard" in HazardReasoningEngine.evaluate_cascade_risks()


def test_ai_confidence_xai_and_hypotheses():
    """Test du moteur de confiance multi-modèles (10 modèles), de l'IA explicable XAI et des hypothèses."""
    conf = ConfidenceEngine.evaluate_multi_model_confidence()
    assert len(conf["models_consulted"]) == 10
    assert "GraphCast" in conf["models_consulted"]

    unc = UncertaintyEngine.quantify_uncertainty()
    assert unc["uncertainty_level"] == "MODERATE"

    xai = ExplainableAIEngine.explain_recommendation("Red Warning Surge")
    assert len(xai["physical_laws_involved"]) >= 2
    assert "observed_evidence" in xai

    hypo = HypothesisGenerator.generate_hypothesis("rapid_intensification")
    assert "hypothesis" in hypo


def test_recommendations_briefings_and_dashboard():
    """Test du moteur de recommandations sectorielles, des bulletins et du tableau de bord AWCI."""
    recs = RecommendationEngine.generate_sectorial_recommendations()
    assert "civil_protection" in recs
    assert "air_traffic" in recs

    bull = AIDecisionSupport.generate_decision_bulletin()
    assert bull["priority"] == "HIGH"

    dialog = ScientificDialogEngine.process_user_query("Explain jet stream")
    assert dialog["confidence_score_pct"] == 95.0

    briefing = ExecutiveBriefingGenerator.generate_full_executive_briefing()
    assert "meteorology_briefing" in briefing
    assert "executive_summary" in briefing

    dash = AWCI_AIDashboard.get_dashboard_metadata()
    assert dash["workspace_name"] == "AUTONOMOUS AI METEOROLOGIST & EARTH SYSTEM EXPERT WORKSPACE"


def test_query_engine_ai_expert_queries():
    """Test des requêtes du ScientificQueryEngine pour le Météorologiste Virtuel autonome."""
    q_engine = ScientificQueryEngine()

    # CORRECTED: used to claim a specific fabricated "today's" synoptic
    # situation (a named North Atlantic cyclone deepening at +40
    # hPa/24h, CAPE 1800 J/kg) regardless of the actual date or any
    # real forecast run.
    r1 = q_engine.ask("Explain today's forecast")
    assert r1["workspace_name"] == "AUTONOMOUS AI METEOROLOGIST & EARTH SYSTEM EXPERT WORKSPACE"
    assert r1["is_real_data"] is False

    r2 = q_engine.ask("Why is heavy rain expected")
    assert "PWV" in r2["physical_explanation"]

    r3 = q_engine.ask("Which model is most reliable")
    assert "GraphCast" in r3["recommended_best_model"]

    # CORRECTED: used to claim a fixed "Ensemble Spread = 2.1 sigma"
    # and "uncertainty_level: MODERATE" as if reporting a real current
    # ensemble run.
    r4 = q_engine.ask("Show uncertainty")
    assert r4["widget_type"] == "UncertaintyQuantificationViewer"
    assert r4["uncertainty_level"] is None

    # CORRECTED: used to claim a specific fabricated emergency response
    # plan (named barrier closures, a "secteur 4" evacuation) and
    # "priority: HIGH" regardless of whether any real hazard was
    # detected.
    r5 = q_engine.ask("Recommend emergency actions")
    assert r5["widget_type"] == "SectorialRecommendationViewer"
    assert r5["priority"] is None

    r6 = q_engine.ask("Generate operational briefing")
    assert r6["report_type"] == "Executive Briefing"
