"""
Atmospheric Complexity Framework (ACF)

Global Operational Hydrology, Flood Forecasting & Water Resources Test Suite (MISSION ACF-033)
"""

from acf.hydrology.core.hydro_db import HydrologyDatabase
from acf.hydrology.drought.drought_engine import HydrologicalDroughtEngine
from acf.hydrology.flooding.flood_engine import FloodForecastEngine
from acf.hydrology.models.hydro_models import HYDROLOGICAL_MODELS_REGISTRY, HydrologicalModelEngine
from acf.hydrology.observations.hydro_obs import HydrologicalObservationEngine
from acf.hydrology.runoff.runoff_engine import RunoffEngine
from acf.hydrology.soil_groundwater.soil_groundwater import GroundwaterEngine, SoilHydrologyEngine
from acf.science.query_engine import ScientificQueryEngine


def test_hydrology_database_core():
    """Test du noyau hydrologique et de calcul du rayon hydraulique Rh et bilan Delta S."""
    rh = HydrologyDatabase.hydraulic_radius_m(wetted_area_m2=20.0, wetted_perimeter_m=10.0)
    assert abs(rh - 2.0) < 1e-4

    delta_s = HydrologyDatabase.water_balance(precipitation_mm=100.0, evapotranspiration_mm=40.0, runoff_mm=35.0)
    assert abs(delta_s - 25.0) < 1e-4

    seine = HydrologyDatabase.get_watershed("seine_basin")
    assert seine is not None
    assert seine.major_river == "Seine"


def test_runoff_and_routing_engine():
    """Test de l'infiltration (SCS Curve Number) et du routage de crue (Muskingum)."""
    scs = RunoffEngine.scs_curve_number_runoff(precipitation_mm=80.0, curve_number=75.0)
    assert scs["runoff_mm"] > 10.0
    assert scs["initial_abstraction_mm"] > 0.0

    q_out = RunoffEngine.muskingum_routing(
        inflow_i0=100.0, inflow_i1=150.0, outflow_q0=90.0, k_hours=12.0, x_factor=0.2, dt_hours=3.0
    )
    assert q_out > 80.0


def test_hydrological_models_registry():
    """Test du registre des modèles numériques hydrologiques (LISFLOOD, HEC-HMS, HEC-RAS)."""
    assert len(HYDROLOGICAL_MODELS_REGISTRY) >= 4

    lisflood = HydrologicalModelEngine.get_model("lisflood")
    assert lisflood is not None
    assert "EFAS" in lisflood.strengths[0] or "Copernicus" in lisflood.institution

    ras = HydrologicalModelEngine.get_model("hec_ras")
    assert ras is not None
    assert "Saint-Venant" in ras.governing_equations


def test_flood_forecast_engine():
    """Test de l'évaluation du risque de crue éclair et période de retour."""
    t_return = FloodForecastEngine.return_period_weibull(rank=1, total_years=99)
    assert abs(t_return - 100.0) < 1e-4

    flash = FloodForecastEngine().evaluate_flash_flood_risk(
        precip_3h_mm=65.0, soil_saturation_pct=90.0, basin_slope_m_km=15.0
    )
    assert flash["alert_color"] == "RED"
    assert "CRITICAL" in flash["risk_level"]


def test_soil_and_groundwater_engine():
    """Test des calculs d'humidité du sol et de la loi de Darcy."""
    soil = SoilHydrologyEngine.soil_water_status(moisture_pct=25.0, field_capacity_pct=30.0, wilting_point_pct=10.0)
    assert soil["available_water_pct"] == 75.0

    darcy = GroundwaterEngine.darcy_flux_m_s(hydraulic_conductivity_m_s=1e-4, hydraulic_gradient_dh_dl=-0.02)
    assert darcy > 0.0


def test_hydrological_drought_engine():
    """Test de la classification de sécheresse SPI et SDI."""
    spi = HydrologicalDroughtEngine.classify_spi_drought(spi_value=-2.3)
    assert spi["drought_category"] == "Extreme Drought"

    sdi = HydrologicalDroughtEngine.evaluate_basin_drought_status(
        monthly_streamflow_m3_s=[10.0], mean_streamflow_m3_s=50.0
    )
    assert "Emergency" in sdi["status"]


def test_hydrological_observation_engine():
    """Test de l'ingestion d'observations de jaugeage de rivière et humidité du sol SMAP."""
    gauge = HydrologicalObservationEngine.get_river_gauge_reading("H5201010")
    assert gauge["river_name"] == "Seine"
    assert gauge["discharge_m3_s"] == 340.0

    smap = HydrologicalObservationEngine.get_satellite_smap_moisture(48.8, 2.3)
    assert smap["volumetric_soil_moisture_cm3_cm3"] == 0.24


def test_query_engine_phase17_hydrology_questions():
    """Test du ScientificQueryEngine sur les requêtes hydrologiques de la mission ACF-033."""
    q_engine = ScientificQueryEngine()

    r1 = q_engine.ask("Show rivers")
    assert r1["layer_type"] == "river_network_layer"

    r2 = q_engine.ask("Show flood risk")
    assert r2["layer_type"] == "flood_inundation_layer"

    r3 = q_engine.ask("Show groundwater")
    assert r3["layer_type"] == "groundwater_layer"

    r4 = q_engine.ask("Show drought")
    assert r4["layer_type"] == "drought_index_layer"

    r5 = q_engine.ask("Compare HEC-HMS and LISFLOOD")
    assert "comparison_table" in r5

    r6 = q_engine.ask("Explain runoff")
    assert "SCS" in r6["references"][0] or "CN" in r6["equation"]
