"""
Atmospheric Complexity Framework (ACF)

Climate & Coupled Earth System Engine Test Suite (MISSION ACF-029)
"""

from acf.climate.climate_indices.indices import CLIMATE_INDICES_REGISTRY, ClimateIndicesEngine
from acf.climate.climate_models.models import CLIMATE_MODELS_REGISTRY, ClimateModelEngine
from acf.climate.earth_system.coupling import EarthSystemCoupler
from acf.climate.projection.scenarios import SSP_SCENARIOS_REGISTRY, ClimateScenarioEngine
from acf.climate.reanalysis.database import REANALYSIS_REGISTRY, ReanalysisEngine
from acf.climate.verification.metrics import ClimateVerificationEngine
from acf.science.query_engine import ScientificQueryEngine


def test_climate_models_registry():
    """Test du registre des modèles climatiques du Système Terre."""
    assert len(CLIMATE_MODELS_REGISTRY) >= 5

    cesm2 = ClimateModelEngine.get_model("cesm2")
    assert cesm2 is not None
    assert "CLM5" in cesm2.land_model

    scream = ClimateModelEngine.get_model("scream")
    assert scream is not None
    assert "3.2 km" in scream.spatial_resolution


def test_reanalysis_database_registry():
    """Test de la base de données des réanalyses climatiques."""
    assert len(REANALYSIS_REGISTRY) >= 4

    era5 = ReanalysisEngine.get("era5")
    assert era5 is not None
    assert era5.spatial_resolution_deg == 0.25
    assert "4D-Var" in era5.data_assimilation_system


def test_climate_indices_registry():
    """Test des indices climatiques et modes de téléconnexion."""
    assert len(CLIMATE_INDICES_REGISTRY) >= 5

    enso = ClimateIndicesEngine.get("enso_nino34")
    assert enso is not None
    assert "ONI" in enso.latex_formula

    nao = ClimateIndicesEngine.get("nao")
    assert nao is not None
    assert "Açores" in nao.region or "Islande" in nao.region


def test_ssp_climate_scenarios():
    """Test des scénarios de projections climatiques CMIP6 / SSP."""
    assert len(SSP_SCENARIOS_REGISTRY) == 5

    ssp245 = ClimateScenarioEngine.get("ssp2_45")
    assert ssp245 is not None
    assert ssp245.forcing_2100_wm2 == 4.5
    assert ssp245.co2_concentration_2100_ppm == 600.0


def test_earth_system_coupler():
    """Test des flux de couplage du système Terre."""
    tau = EarthSystemCoupler.ocean_atmosphere_momentum_flux(wind_speed_10m=10.0)
    assert tau > 0.1

    albedo = EarthSystemCoupler.sea_ice_albedo_feedback(ice_concentration=0.5)
    assert 0.3 < albedo < 0.6

    npp = EarthSystemCoupler.net_primary_production_co2_flux(par_radiation=200.0, temp_c=25.0, q_soil=0.5)
    assert npp > 0.0


def test_climate_verification_engine():
    """Test des métriques statistiques climatiques et tendances."""
    anomaly = ClimateVerificationEngine.calculate_anomaly(value=15.5, climatological_mean=14.0)
    assert abs(anomaly - 1.5) < 1e-5

    forecast_anom = [0.5, 1.0, 1.5, 2.0, 2.5]
    obs_anom = [0.4, 1.1, 1.4, 1.9, 2.6]
    acc = ClimateVerificationEngine.anomaly_correlation_coefficient(forecast_anom, obs_anom)
    assert acc > 0.95

    annual_temps = [14.0 + 0.02 * i for i in range(30)]
    trend = ClimateVerificationEngine.calculate_decadal_trend(annual_temps)
    assert abs(trend - 0.20) < 1e-4

    taylor = ClimateVerificationEngine.taylor_diagram_metadata([14.1, 14.5, 15.0], [14.0, 14.4, 14.9])
    assert "correlation" in taylor
    assert "centered_rmse" in taylor


def test_query_engine_phase14_climate_questions():
    """Test le ScientificQueryEngine sur les questions climatiques de la mission ACF-029."""
    q_engine = ScientificQueryEngine()

    # 1. Explain ENSO
    r1 = q_engine.ask("Explain ENSO")
    assert "latex_equation" in r1
    assert "ONI" in r1["latex_equation"]

    # 2. Compare ERA5 and MERRA2
    r2 = q_engine.ask("Compare ERA5 and MERRA2")
    assert "comparison_table" in r2

    # 3. Show CMIP6 projections
    r3 = q_engine.ask("Show CMIP6 projections")
    assert "available_scenarios" in r3

    # 4. Explain SSP2-4.5
    r4 = q_engine.ask("Explain SSP2-4.5")
    assert "forcing_2100" in r4

    # 5. Show drought index
    r5 = q_engine.ask("Show drought index")
    assert "drought_indices" in r5

    # 6. Compare climate models
    r6 = q_engine.ask("Compare climate models")
    assert "models_compared" in r6

    # 7. Explain AMO
    r7 = q_engine.ask("Explain AMO")
    assert "region" in r7

    # 8. Why is NAO positive?
    r8 = q_engine.ask("Why is NAO positive?")
    assert "synoptic_pattern" in r8
