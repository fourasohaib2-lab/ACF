"""
Atmospheric Complexity Framework (ACF)

Global Marine Meteorology, Oceanography & Coastal Hazard Test Suite (MISSION ACF-032)
"""

from acf.ocean.cyclones.cyclones import HurricaneDatabase
from acf.ocean.forecasting.marine_forecaster import MarineForecastEngine
from acf.ocean.models.ocean_models import OCEAN_MODELS_REGISTRY, OceanModelEngine
from acf.ocean.observations.marine_obs import MarineObservationEngine
from acf.ocean.oceanography.ocean_db import OceanDatabase, PhysicalOceanographyEngine
from acf.ocean.waves.wave_models import WAVE_MODELS_REGISTRY, OperationalWaveEngine
from acf.science.query_engine import ScientificQueryEngine


def test_physical_oceanography_engine():
    """Test des calculs physiques océaniques (N², Ekman, Géostrophie)."""
    n2 = PhysicalOceanographyEngine.brunt_vaisala_frequency(d_rho_dz=-0.005)
    assert n2 > 0.0

    w_e = PhysicalOceanographyEngine.ekman_pumping_velocity(curl_tau=1e-7, latitude_deg=45.0)
    assert w_e > 0.0

    v_g = PhysicalOceanographyEngine.geostrophic_current_velocity(dp_dx=10.0, latitude_deg=45.0)
    assert abs(v_g) > 0.0

    atl = OceanDatabase.get_ocean_basin_info("Atlantique")
    assert "Gulf Stream" in atl["currents"]


def test_operational_wave_engine():
    """Test des modèles de vagues spectraux (Hs, Tp, Cg, JONSWAP)."""
    assert len(WAVE_MODELS_REGISTRY) >= 3

    ww3 = OperationalWaveEngine.significant_wave_height_from_spectrum(energy_m0=1.0)
    assert abs(ww3 - 4.0) < 1e-4

    cg = OperationalWaveEngine.wave_group_velocity(peak_period_s=10.0)
    assert 7.0 < cg < 8.0  # ~7.8 m/s

    spec = OperationalWaveEngine.jonswap_spectrum_peak_energy(wind_speed_10m=15.0, fetch_m=100000.0)
    assert spec["significant_wave_height_m"] > 0.5


def test_marine_forecast_engine():
    """Test du moteur de prévision d'état de mer et surcotes."""
    m_engine = MarineForecastEngine()
    ds = m_engine.douglas_sea_state(hs_m=3.5)
    assert "Moderate" in ds["douglas_code"]

    fcst = m_engine.generate_marine_forecast(wind_speed_kts=30.0, fetch_km=150.0, swell_hs_m=2.5)
    assert fcst["combined_significant_wave_height_m"] > 2.5
    assert fcst["rip_current_risk"] == "HIGH"


def test_hurricane_database():
    """Test de la base de données des cyclones tropicaux et échelle Saffir-Simpson."""
    cat5 = HurricaneDatabase.saffir_simpson_category(wind_speed_kt=140.0)
    assert cat5 == 5

    cat1 = HurricaneDatabase.saffir_simpson_category(wind_speed_kt=75.0)
    assert cat1 == 1

    # CORRECTED: used to unconditionally claim a specific Category 4
    # hurricane named "Helene" was currently active, with 0 real
    # NHC/JTWC best-track feed connected.
    active = HurricaneDatabase.get_active_cyclones()
    assert active == []


def test_ocean_models_registry():
    """Test du registre des modèles de circulation océanique (NEMO, HYCOM, ROMS)."""
    assert len(OCEAN_MODELS_REGISTRY) >= 3

    nemo = OceanModelEngine.get_model("nemo")
    assert nemo is not None
    assert "ORCA" in nemo.spatial_resolution or "European" in nemo.institution


def test_marine_observation_engine():
    """Test de l'ingestion d'observations ARGO et bouées NDBC."""
    argo = MarineObservationEngine.get_sample_argo_profile("6902741")
    assert len(argo.depths_m) == 8
    assert argo.depths_m[-1] == 2000.0

    # CORRECTED: used to claim to "decode" a real buoy message while
    # every reading was fixed regardless of buoy_id, with no real
    # NDBC feed connected.
    buoy = MarineObservationEngine.decode_buoy_report("41001")
    assert buoy["significant_wave_height_m"] is None
    assert buoy["status"] == "NOT_DECODED_NO_REAL_NDBC_FEED_CONNECTED"
    assert buoy["buoy_id"] == "41001"  # genuinely echoed


def test_query_engine_phase16_marine_questions():
    """Test du ScientificQueryEngine sur les requêtes océaniques de la mission ACF-032."""
    q_engine = ScientificQueryEngine()

    r1 = q_engine.ask("Show waves")
    assert r1["layer_type"] == "wave_height_layer"

    r2 = q_engine.ask("Show SST")
    assert r2["layer_type"] == "sst_layer"

    r3 = q_engine.ask("Show ocean currents")
    assert r3["layer_type"] == "ocean_currents_layer"

    r4 = q_engine.ask("Show storm surge")
    assert r4["layer_type"] == "storm_surge_layer"

    r5 = q_engine.ask("Show cyclone")
    assert r5["widget_type"] == "TropicalCycloneTracker"

    r6 = q_engine.ask("Compare WaveWatch and WAM")
    assert "comparison_table" in r6

    r7 = q_engine.ask("Explain Ekman Transport")
    assert "M_e" in r7["equation"]
