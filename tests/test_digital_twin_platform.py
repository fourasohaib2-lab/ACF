"""
Atmospheric Complexity Framework (ACF)

Global Integrated Earth System Digital Twin Platform Test Suite (MISSION ACF-036)
"""

from acf.digital_twin.planet_state import GlobalEarthState, PlanetState
from acf.digital_twin.state_vector import GlobalEarthStateVector
from acf.digital_twin.digital_twin_engine import DigitalTwinEngine, SimulationState
from acf.digital_twin.synchronization.earth_synchronizer import EarthSynchronizationEngine, CouplingReport, SynchronizationReport
from acf.digital_twin.coupling.atmosphere_ocean import AtmosphereOceanCouplingEngine
from acf.digital_twin.coupling.earthquake_tsunami import EarthquakeTsunamiCouplingEngine
from acf.digital_twin.coupling.space_weather_atmosphere import SpaceWeatherAtmosphereCouplingEngine
from acf.digital_twin.events.cascade_engine import CascadeRiskEngine, RiskCascadeGraph
from acf.digital_twin.knowledge_graph.earth_graph import PlanetaryKnowledgeGraph
from acf.digital_twin.ai.digital_reasoning import DigitalTwinReasoningEngine
from acf.digital_twin.scenarios.future_projection import PlanetaryScenarioEngine
from acf.digital_twin.visualization.digital_twin_dashboard import PlanetaryDashboard
from acf.digital_twin.operations.operations_center import EarthOperationsCenter, OperationalSituation, GlobalAlertBoard
from acf.digital_twin.reports.planetary_report import PlanetaryReportGenerator
from acf.science.query_engine import ScientificQueryEngine


def test_digital_twin_engine_and_state_vector():
    """Test du vecteur d'état global et du moteur Digital Twin."""
    vec = GlobalEarthStateVector(temp_2m_c=16.0, cape_j_kg=1500.0, sst_c=19.0, kp_index=5.0)
    d = vec.to_dict()
    assert d["atmosphere"]["temp_2m_c"] == 16.0
    assert d["space_weather"]["kp_index"] == 5.0

    engine = DigitalTwinEngine()
    cycle = engine.run_digital_twin_cycle(lead_time_horizon="+48h")
    assert "DestinE Equivalent" in cycle["engine"]
    assert cycle["simulation"]["horizon"] == "+48h"


def test_earth_synchronization_engine():
    """Test du moteur de synchronisation et des rapports de couplage."""
    sync_report = EarthSynchronizationEngine.synchronize_all_components()
    assert sync_report.coupled_domains_count >= 5
    assert "EXCELLENT" in sync_report.synchronization_quality


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
    """Test du moteur de risques en cascade multi-domaines (Cyclone, Séisme, Tempête solaire)."""
    cascades = CascadeRiskEngine.evaluate_active_cascades()
    assert cascades["active_cascades_count"] >= 4
    assert "Cyclone" in cascades["cascades"][0]["trigger"]


def test_planetary_knowledge_graph_and_ai_reasoning():
    """Test du graphe de connaissances planétaire et du moteur de raisonnement d'IA."""
    nodes = PlanetaryKnowledgeGraph.get_domain_nodes()
    assert "Atmosphere" in nodes
    assert "Space Weather" in nodes

    link = PlanetaryKnowledgeGraph.explain_planetary_link("Space Weather", "Atmosphere")
    assert "Joule heating" in link["physical_coupling_explanation"]

    ai_exp = DigitalTwinReasoningEngine.explain_system_event("Tropical Cyclone")
    assert ai_exp["ai_confidence_pct"] > 90.0


def test_scenario_projections_and_dashboard():
    """Test des projections scénarisées multi-échelles et du tableau de bord AWCI."""
    weather_scen = PlanetaryScenarioEngine.run_scenario_projection(horizon="+48h")
    assert "GraphCast" in weather_scen["predictive_model_used"]

    climate_scen = PlanetaryScenarioEngine.run_scenario_projection(horizon="+100yr", ssp_scenario="SSP2-4.5")
    assert "CMIP6" in climate_scen["predictive_model_used"]
    assert climate_scen["projected_global_temp_change_c"] == 2.7

    dash = PlanetaryDashboard.get_dashboard_metadata()
    assert dash["workspace_name"] == "PLANETARY DIGITAL TWIN"


test_operations_center_and_briefing_reports = lambda: (
    _test_ops_and_reports()
)


def _test_ops_and_reports():
    ops = EarthOperationsCenter.get_global_operations_status()
    assert ops.total_red_alerts >= 1

    report = PlanetaryReportGenerator.generate_planetary_briefing_markdown()
    assert "# Global Earth System Digital Twin Daily Report" in report


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
