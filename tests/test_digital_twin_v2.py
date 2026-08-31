"""
Atmospheric Complexity Framework (ACF)

Complete Earth Digital Twin Platform Test Suite (MISSION ACF-UI-010)
"""

from acf.ai.digital_twin.twin_assistant import AIDigitalTwinAssistant
from acf.digital_twin.boundary_conditions import BoundaryConditionsManager
from acf.digital_twin.calibration_engine import CalibrationEngine
from acf.digital_twin.coupling_engine import CouplingEngine
from acf.digital_twin.earth_state import EarthState
from acf.digital_twin.earth_twin_core import EarthTwinCore
from acf.digital_twin.experiment_manager import ExperimentManager
from acf.digital_twin.feedback_engine import FeedbackEngine
from acf.digital_twin.geoengineering_lab.geoengineering_lab import GeoengineeringLab
from acf.digital_twin.planet_model import PlanetModel
from acf.digital_twin.planetary_dashboard import PlanetaryDashboard
from acf.digital_twin.planetary_limits.planetary_boundaries import PlanetaryBoundariesSimulator
from acf.digital_twin.scenario_engine import DigitalTwinScenarioEngine
from acf.digital_twin.simulation_manager import SimulationManager
from acf.digital_twin.twin_visualizer import DigitalTwinVisualizer


def test_earth_twin_core_and_state():
    """Test du cœur d'orchestration et du vecteur d'état à 6 sphères."""
    core = EarthTwinCore()
    res = core.run_full_earth_twin_cycle()
    assert res["digital_twin_status"] == "EARTH_DIGITAL_TWIN_OPERATIONAL"
    assert res["earth_state"]["coupled_spheres_count"] == 6

    state = EarthState()
    summary = state.get_state_vector_summary()
    assert summary["co2_ppm"] == 422.5
    assert summary["status"] == "EARTH_STATE_SYNCHRONIZED"


def test_couplings_and_scenario_engine():
    """Test du moteur de couplage inter-sphères et des scénarios CMIP6 / +2°C."""
    coup = CouplingEngine.compute_couplings()
    assert coup["coupling_status"] == "FULL_COUPLING_COMPUTED"
    assert "Heat Flux" in coup["atmosphere_ocean_coupling"]

    ssp2 = DigitalTwinScenarioEngine.run_scenario("SSP2-4.5")
    assert ssp2["status"] == "SCENARIO_SIMULATION_SUCCESS"

    warm2c = DigitalTwinScenarioEngine.run_scenario("CUSTOM_+2C_WARMING")
    assert warm2c["projections"]["temperature_anomaly_k"] == 2.1
    assert warm2c["projections"]["sea_level_rise_m"] == 0.45


def test_planetary_boundaries_and_geoengineering():
    """Test du simulateur des 9 limites planétaires et du laboratoire de géo-ingénierie."""
    limits = PlanetaryBoundariesSimulator.audit_planetary_boundaries()
    assert limits["climate_change"]["status"] == "TRANSGRESSED"
    assert limits["overall_audit_summary"] == "6_OF_9_BOUNDARIES_TRANSGRESSED"

    # CORRECTED: used to claim a fixed "-0.45K cooling"/"4.2 benefit-
    # cost ratio" regardless of the injection amount (physically
    # wrong - a real response scales with dose) with no climate model
    # connected. Geoengineering is a contested policy topic; a fake
    # benefit-cost ratio could misinform a real argument.
    geo = GeoengineeringLab.simulate_stratospheric_aerosol_injection(5.0)
    assert geo["status"] == "NOT_SIMULATED_NO_CLIMATE_MODEL_CONNECTED"
    assert geo["cooling_effect_k"] is None
    assert geo["benefit_cost_ratio"] is None
    assert len(geo["known_risk_categories"]) >= 3


def test_ai_digital_twin_assistant_and_experiments():
    """Test de l'assistant IA prospective et de la gestion des expériences."""
    ai_res = AIDigitalTwinAssistant.analyze_scenario_query("Que se passe-t-il si la température augmente de 3°C ?")
    assert ai_res["status"] == "DIGITAL_TWIN_SIMULATION_COMPLETE"
    assert ai_res["ai_confidence_score"] == 84.0
    assert "Atmosphere" in ai_res["sphere_impacts"]

    exp = ExperimentManager.create_experiment("EXP-2026-001")
    assert exp["status"] == "EXPERIMENT_EXECUTED"
    assert exp["duration_years"] == 100

    vis = DigitalTwinVisualizer.get_visualization_modes()
    assert vis["status"] == "VISUALIZER_READY"
    assert len(vis["modes"]) >= 5


def test_ancillary_digital_twin_modules():
    """Test des modules annexes (Feedback, Calibration, Dashboard, PlanetModel)."""
    fb = FeedbackEngine.evaluate_feedbacks()
    assert fb["status"] == "FEEDBACKS_EVALUATED"

    # CORRECTED: used to claim a fabricated "0.04 RMSE"/"128
    # parameters tuned" with no real calibration against observations.
    cal = CalibrationEngine.calibrate_twin()
    assert cal["status"] == "NOT_CALIBRATED_NO_OBSERVATION_DATA_PROVIDED"
    assert cal["calibration_error_rmse"] is None

    # CORRECTED: used to claim a fabricated "74.5/100" planetary
    # health index (the same fake number independently found in
    # EarthHealthMonitor, fixed earlier this session).
    dash = PlanetaryDashboard.get_dashboard_summary()
    assert dash["status"] == "NOT_ACTIVE_NO_EXPERIMENT_TRACKER_CONNECTED"
    assert dash["planetary_health_index"] is None

    pm = PlanetModel.get_planet_parameters()
    assert pm["radius_km"] == 6371.0

    sm = SimulationManager.execute_simulation()
    assert sm["execution_status"] == "RUNNING_COMPUTE"
    # BoundaryConditionsManager: solar_constant_w_m2 is a genuine
    # physical constant, kept unchanged.
    assert BoundaryConditionsManager.get_boundary_conditions()["solar_constant_w_m2"] == 1361.0
