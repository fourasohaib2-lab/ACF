"""
Atmospheric Complexity Framework (ACF)

Global Integrated Earth System Digital Twin Platform Test Suite (MISSION ACF-036)
"""

from acf.digital_twin.ai.digital_reasoning import DigitalTwinReasoningEngine
from acf.digital_twin.coupling.atmosphere_ocean import AtmosphereOceanCouplingEngine
from acf.digital_twin.coupling.earthquake_tsunami import EarthquakeTsunamiCouplingEngine
from acf.digital_twin.coupling.space_weather_atmosphere import SpaceWeatherAtmosphereCouplingEngine
from acf.digital_twin.digital_twin_engine import DigitalTwinEngine
from acf.digital_twin.events.cascade_engine import CascadeRiskEngine
from acf.digital_twin.knowledge_graph.earth_graph import PlanetaryKnowledgeGraph
from acf.digital_twin.operations.operations_center import EarthOperationsCenter
from acf.digital_twin.reports.planetary_report import PlanetaryReportGenerator
from acf.digital_twin.scenarios.future_projection import PlanetaryScenarioEngine
from acf.digital_twin.state_vector import GlobalEarthStateVector
from acf.digital_twin.synchronization.earth_synchronizer import EarthSynchronizationEngine
from acf.digital_twin.visualization.digital_twin_dashboard import PlanetaryDashboard
from acf.science.query_engine import ScientificQueryEngine


def test_digital_twin_engine_and_state_vector():
    """Test du vecteur d'état global et du moteur Digital Twin."""
    vec = GlobalEarthStateVector(temp_2m_c=16.0, cape_j_kg=1500.0, sst_c=19.0, kp_index=5.0)
    d = vec.to_dict()
    assert d["atmosphere"]["temp_2m_c"] == 16.0
    assert d["space_weather"]["kp_index"] == 5.0

    # CORRECTED: every field of GlobalEarthStateVector used to default
    # to a specific fabricated value (temp_2m_c=15.2, sst_c=18.5,
    # ai_model_active="GraphCast + NeuralGCM Ensemble", etc.), so a
    # bare GlobalEarthStateVector() (as digital_twin.planet_state.
    # GlobalEarthState's own default_factory constructs) silently
    # produced a complete fake "current state of planet Earth" with no
    # real observation behind it.
    empty_vec = GlobalEarthStateVector()
    empty_d = empty_vec.to_dict()
    assert empty_d["atmosphere"]["temp_2m_c"] is None
    assert empty_d["ai"]["ai_model_active"] is None
    assert empty_d["geology"]["max_recent_earthquake_mw"] is None
    # Fields genuinely supplied still come through unaffected.
    assert d["ocean"]["sst_c"] == 19.0

    # CORRECTED: progress_pct/simulation_id used to unconditionally
    # claim a completed cycle (100.0, a fixed literal id) with no real
    # assimilation/forecast cycle ever run.
    engine = DigitalTwinEngine()
    cycle = engine.run_digital_twin_cycle(lead_time_horizon="+48h")
    assert "DestinE Equivalent" in cycle["engine"]
    assert cycle["simulation"]["horizon"] == "+48h"  # genuinely echoed
    assert cycle["simulation"]["progress"] is None
    assert cycle["status"] == "NOT_RUN_NO_ASSIMILATION_FORECAST_CYCLE_CONNECTED"


def test_earth_synchronization_engine():
    """Test du moteur de synchronisation et des rapports de couplage."""
    # CORRECTED: used to unconditionally claim "SYNCHRONIZED" status
    # and specific fabricated coupling-strength percentages
    # (98.5/99.0/97.2/100.0/96.8) and "EXCELLENT (100% CONVERGENCE)"
    # regardless of any real cross-domain data exchange. The domain
    # pairs/flux_variable names are a genuine static declared coupling
    # scope, kept.
    sync_report = EarthSynchronizationEngine.synchronize_all_components()
    assert sync_report.coupled_domains_count >= 5
    assert sync_report.synchronization_quality == "NOT_SYNCHRONIZED_NO_REAL_DATA_EXCHANGE_CONNECTED"
    assert all(r.coupling_status == "NOT_SYNCHRONIZED" for r in sync_report.coupling_reports)
    assert all(r.coupling_strength_pct is None for r in sync_report.coupling_reports)


def test_cross_domain_coupling_physics():
    """Test des couplages physique Atmosphère-Océan, Séisme-Tsunami et Temps Spatial-Atmosphère."""
    tau = AtmosphereOceanCouplingEngine.momentum_flux_tau_n_m2(wind_speed_10m_ms=15.0)
    assert tau > 0.3  # N/m²

    qlh = AtmosphereOceanCouplingEngine.latent_heat_flux_w_m2(wind_speed_ms=10.0, q_sea=0.018, q_air=0.012)
    assert qlh > 100.0  # W/m²

    tsunami_e = EarthquakeTsunamiCouplingEngine.seafloor_uplift_energy_joules(seismic_moment_m0_nm=1e22)
    assert tsunami_e > 1e20

    joule_gw = SpaceWeatherAtmosphereCouplingEngine.joule_heating_rate_gw(kp_index=8.0)
    assert joule_gw == 960.0  # 15 * 64 GW


def test_cascade_risk_engine():
    """
    Test du moteur de risques en cascade multi-domaines (Cyclone, Séisme, Tempête solaire).

    CORRECTED: used to unconditionally claim the static reference
    catalog of KNOWN cascade patterns was the set of cascades
    "actively" detected right now, with no real hazard-detection
    pipeline connected. The catalog itself (known_cascade_patterns) is
    a genuine, honest reference knowledge base and is kept.
    """
    cascades = CascadeRiskEngine.evaluate_active_cascades()
    assert cascades["active_cascades_count"] == 0
    assert cascades["cascades"] == []
    assert cascades["known_cascade_patterns_count"] >= 4
    assert "Cyclone" in cascades["known_cascade_patterns"][0]["trigger"]
    assert cascades["status"] == "NOT_DETECTED_NO_LIVE_HAZARD_DATA_CONNECTED"


def test_planetary_knowledge_graph_and_ai_reasoning():
    """Test du graphe de connaissances planétaire et du moteur de raisonnement d'IA."""
    nodes = PlanetaryKnowledgeGraph.get_domain_nodes()
    assert "Atmosphere" in nodes
    assert "Space Weather" in nodes

    link = PlanetaryKnowledgeGraph.explain_planetary_link("Space Weather", "Atmosphere")
    assert "Joule heating" in link["physical_coupling_explanation"]

    # CORRECTED: the branch selection and explanatory text are genuine
    # (real physical thresholds), but this used to also claim a fixed
    # fabricated "ai_confidence_pct" (94.2 for this branch) regardless
    # of any real evidence - no calibrated confidence model exists.
    ai_exp = DigitalTwinReasoningEngine.explain_system_event("Tropical Cyclone")
    assert ai_exp["ai_confidence_pct"] is None
    assert "26.5" in ai_exp["explanation"]


def test_scenario_projections_and_dashboard():
    """Test des projections scénarisées multi-échelles et du tableau de bord AWCI."""
    weather_scen = PlanetaryScenarioEngine.run_scenario_projection(horizon="+48h")
    assert "GraphCast" in weather_scen["predictive_model_used"]

    climate_scen = PlanetaryScenarioEngine.run_scenario_projection(horizon="+100yr", ssp_scenario="SSP2-4.5")
    assert "CMIP6" in climate_scen["predictive_model_used"]
    assert climate_scen["projected_global_temp_change_c"] == 2.7

    dash = PlanetaryDashboard.get_dashboard_metadata()
    assert dash["workspace_name"] == "PLANETARY DIGITAL TWIN"


def test_operations_center_and_briefing_reports():
    _test_ops_and_reports()


def _test_ops_and_reports():
    """
    CORRECTED: get_global_operations_status() used to unconditionally
    report 3 fixed fabricated situations (a fake Category 4 typhoon
    naming real places, a fake Mw 7.2 earthquake) with a frozen fake
    timestamp; generate_planetary_briefing_markdown() used to report a
    fake +1.15°C anomaly and fake active cyclones/earthquake for ANY
    call, with 0 real domain data connected in either case.
    """
    ops = EarthOperationsCenter.get_global_operations_status()
    assert ops.total_red_alerts == 0
    assert ops.active_situations == []

    report = PlanetaryReportGenerator.generate_planetary_briefing_markdown()
    assert "# Global Earth System Digital Twin Daily Report" in report
    assert "NOT SYNCHRONIZED" in report
    assert "+1.15" not in report


def test_query_engine_digital_twin_queries():
    """Test des requêtes du ScientificQueryEngine pour le Digital Twin."""
    q_engine = ScientificQueryEngine()

    r1 = q_engine.ask("Show Earth Twin")
    assert r1["workspace_name"] == "PLANETARY DIGITAL TWIN"

    r2 = q_engine.ask("Show Earth Coupling")
    assert r2["widget_type"] == "EarthSynchronizationViewer"

    r3 = q_engine.ask("Show Cascade")
    assert r3["layer_type"] == "multi_hazard_cascade_layer"

    r4 = q_engine.ask("Explain Scenario")
    assert "+100yr" in r4["available_horizons"]
