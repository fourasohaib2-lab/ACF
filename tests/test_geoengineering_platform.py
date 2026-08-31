"""
Atmospheric Complexity Framework (ACF)

Global Geoengineering, Climate Intervention & Planetary Boundaries Platform Test Suite (MISSION ACF-040)
"""

from acf.geoengineering.awci_geoengineering_dashboard import PlanetaryBoundariesDashboard
from acf.geoengineering.carbon_cycle import CarbonCycleEngine, CarbonFluxes, CarbonReservoirs
from acf.geoengineering.carbon_removal import CarbonRemovalEngine, CDRTechniqueResult
from acf.geoengineering.climate_ai import ClimateDecisionEngine
from acf.geoengineering.climate_restoration import ClimateRestorationEngine, EcosystemRestorationProject
from acf.geoengineering.greenhouse_gases import GHGProperties, GreenhouseGasEngine
from acf.geoengineering.planetary_boundaries import BoundaryAssessment, PlanetaryBoundaryEngine
from acf.geoengineering.scenario_engine import ClimateScenarioEngine, SSPScenario
from acf.geoengineering.solar_radiation_management import SolarRadiationManagementEngine, SRMResult
from acf.science.query_engine import ScientificQueryEngine


def test_planetary_boundaries_engine():
    """Test de l'évaluation des 9 limites planétaires (Rockström / Steffen)."""
    boundary = PlanetaryBoundaryEngine.get_boundary("climate_change")
    assert boundary is not None
    assert boundary.is_transgressed is True
    assert boundary.current_value == 425.0

    assessment = PlanetaryBoundaryEngine.evaluate_planetary_boundaries()
    assert isinstance(assessment, BoundaryAssessment)
    assert assessment.total_boundaries_count == 9
    assert assessment.transgressed_count >= 6


def test_solar_radiation_management_engine():
    """Test de la modélisation des techniques SRM (SAI et MCB)."""
    sai = SolarRadiationManagementEngine.simulate_stratospheric_aerosol_injection(so2_injection_megatons_per_year=5.0)
    assert isinstance(sai, SRMResult)
    assert sai.radiative_forcing_w_m2 < 0.0
    assert sai.global_temperature_cooling_k > 1.0

    mcb = SolarRadiationManagementEngine.simulate_marine_cloud_brightening(sea_salt_injection_rate_t_s=100.0)
    assert mcb.radiative_forcing_w_m2 < 0.0


def test_carbon_removal_and_restoration_engines():
    """Test des techniques d'élimination du CO2 (DAC, ERW) et de la restauration des écosystèmes."""
    dac = CarbonRemovalEngine.evaluate_direct_air_capture(capacity_gt_co2=1.0)
    assert isinstance(dac, CDRTechniqueResult)
    assert dac.durability_years == 10000.0

    erw = CarbonRemovalEngine.evaluate_enhanced_weathering(rock_dust_gt=5.0)
    assert erw.annual_removal_capacity_gt_co2 > 1.0

    mangrove = ClimateRestorationEngine.evaluate_mangrove_restoration(hectares=100000.0)
    assert isinstance(mangrove, EcosystemRestorationProject)
    assert mangrove.annual_sequestration_t_co2_yr > 1.0e6


def test_greenhouse_gas_and_carbon_cycle_engines():
    """Test du forçage radiatif des GES et du cycle du carbone à 5 réservoirs."""
    forcing_co2 = GreenhouseGasEngine.co2_radiative_forcing(c_ppm=425.0)
    assert 2.0 < forcing_co2 < 3.0

    ghg_prop = GreenhouseGasEngine.get_ghg_properties("sf6")
    assert isinstance(ghg_prop, GHGProperties)
    assert ghg_prop.gwp_100 == 23500.0

    cycle = CarbonCycleEngine.get_current_state()
    assert "reservoirs" in cycle
    assert isinstance(cycle["reservoirs"], CarbonReservoirs)
    assert isinstance(cycle["fluxes"], CarbonFluxes)
    assert cycle["annual_atmospheric_co2_growth_gtc"] > 0.0


def test_climate_ai_and_scenario_engine():
    """Test du moteur de décision par IA et des projections d'émissions CMIP6/SSP."""
    decision = ClimateDecisionEngine.evaluate_intervention_strategy(target_cooling_k=1.0)
    assert "7_scientific_report" in decision
    assert decision["target_cooling_k"] == 1.0

    ssp = ClimateScenarioEngine.get_scenario("ssp2_45")
    assert isinstance(ssp, SSPScenario)
    assert ssp.warming_mean_2100_c == 2.7


def test_geoengineering_dashboard_and_query_engine():
    """Test du tableau de bord AWCI Geoengineering et des requêtes du Query Engine."""
    meta = PlanetaryBoundariesDashboard.get_dashboard_metadata()
    assert meta["workspace_name"] == "PLANETARY BOUNDARIES & CLIMATE CONTROL CENTER"

    q_engine = ScientificQueryEngine()

    r1 = q_engine.ask("Show Planetary Boundaries")
    assert r1["workspace_name"] == "PLANETARY BOUNDARIES & CLIMATE CONTROL CENTER"

    r2 = q_engine.ask("Show CO2 Removal")
    assert r2["widget_type"] == "GeoengineeringTechniquesViewer"

    r3 = q_engine.ask("Show Carbon Cycle")
    assert r3["widget_type"] == "CarbonCycleReservoirViewer"

    r4 = q_engine.ask("Show SSP")
    assert r4["widget_type"] == "ClimateScenarioViewer"
