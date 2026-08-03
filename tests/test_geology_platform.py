"""
Atmospheric Complexity Framework (ACF)

Global Geology, Geophysics, Seismology & Natural Hazards Test Suite (MISSION ACF-035)
"""

from acf.geology.geology_database import GeologyDatabase, EarthLayer
from acf.geology.tectonic_plates import PlateDatabase, Plate
from acf.geology.faults import FaultDatabase, FaultSegment
from acf.geology.seismology import EarthquakeDatabase, MomentTensor, SeismologyEngine
from acf.geology.seismic_waves import SeismicWaveEngine
from acf.geology.earthquake_warning import EarthquakeWarningEngine
from acf.geology.volcanoes import VolcanoDatabase, Volcano
from acf.geology.volcanic_physics import VolcanicPhysicsEngine
from acf.geology.tsunami_engine import TsunamiForecastEngine
from acf.geology.landslides import SlopeStabilityEngine
from acf.geology.geodesy import GeodesyEngine
from acf.geology.gravity import GravityEngine
from acf.geology.geomagnetism import SolidEarthGeomagneticEngine
from acf.geology.hazards import HazardEngine
from acf.geology.observatories import GeologicalObservatoryEngine, GEOLOGICAL_OBSERVATORIES_REGISTRY
from acf.geology.awci_geology_dashboard import GeologyCenterDashboard
from acf.geology.geology_ai import GeologicalReasoningEngine
from acf.science.query_engine import ScientificQueryEngine


def test_geology_database_prem_layers():
    """Test du modèle de structure interne de la Terre PREM (Croûte à Noyau interne)."""
    assert len(GeologyDatabase.list_layers()) >= 6

    crust = GeologyDatabase.get_layer("continental_crust")
    assert crust is not None
    assert crust.density_g_cm3 == 2.7
    assert crust.vp_km_s == 6.3

    inner_core = GeologyDatabase.get_layer("inner_core")
    assert inner_core is not None
    assert inner_core.depth_bottom_km == 6371.0


def test_tectonic_plates():
    """Test des plaques tectoniques mondiales (Pacifique, Eurasie, Afrique, Nazca)."""
    assert len(PlateDatabase.list_plates()) >= 4

    pac = PlateDatabase.get_plate("pacific_plate")
    assert pac is not None
    assert pac.velocity_cm_year == 8.5
    assert "Japan Trench" in pac.subduction_zones


def test_fault_database():
    """Test des failles géologiques majeures (San Andreas, Anatolienne, Fosse du Japon)."""
    assert len(FaultDatabase.list_faults()) >= 3

    saf = FaultDatabase.get_fault("san_andreas")
    assert saf is not None
    assert saf.slip_rate_mm_year == 35.0
    assert saf.max_credible_magnitude_mw == 8.1


def test_seismology_laws_and_events():
    """Test du calcul de Mw, Gutenberg-Richter, Omori et loi de Bath."""
    mw = SeismologyEngine.moment_magnitude_mw(seismic_moment_m0_nm=5.3e22)
    assert abs(mw - 9.1) < 0.2

    gr_n = SeismologyEngine.gutenberg_richter_frequency(a_value=5.0, b_value=1.0, min_magnitude=5.0)
    assert gr_n == 1.0  # 10^(5 - 5) = 1

    omori_rate = SeismologyEngine.omori_aftershock_rate(time_days=1.0)
    assert omori_rate > 0.0

    bath = SeismologyEngine.bath_law_largest_aftershock(mainshock_mw=9.0)
    assert abs(bath - 7.8) < 1e-4

    eq = EarthquakeDatabase.get_sample_earthquake("US2011TOHOKU")
    assert eq.magnitude_mw == 9.1


def test_seismic_wave_physics():
    """Test de la vitesse des ondes P/S (Vp, Vs), onde de Rayleigh, et temps de parcours."""
    vp = SeismicWaveEngine.p_wave_velocity_m_s(bulk_modulus_k_pa=75e9, shear_modulus_mu_pa=30e9, density_kg_m3=3000.0)
    assert vp > 6000.0  # m/s

    vs = SeismicWaveEngine.s_wave_velocity_m_s(shear_modulus_mu_pa=30e9, density_kg_m3=3000.0)
    assert vs > 3000.0  # m/s

    tt = SeismicWaveEngine.travel_time_p_and_s(distance_km=300.0)
    assert tt["p_arrival_seconds"] == 50.0
    assert tt["s_minus_p_delay_seconds"] > 0.0


def test_earthquake_early_warning():
    """Test du délai d'alerte sismologique précoce EEWS."""
    eew = EarthquakeWarningEngine().calculate_warning_lead_time(distance_epicenter_km=150.0)
    assert eew["warning_lead_time_seconds"] > 10.0
    assert "ACTIVE" in eew["alert_status"]


def test_volcanoes_and_volcanic_physics():
    """Test de la base volcanologique, du modèle de Mogi et de la hauteur du panache éruptif Mastin."""
    assert len(VolcanoDatabase.list_volcanoes()) >= 3

    vesuvius = VolcanoDatabase.get_volcano("vesuvius")
    assert vesuvius is not None
    assert vesuvius.vei_max == 5

    mogi = VolcanicPhysicsEngine.mogi_surface_displacement_m(radial_distance_m=1000.0, chamber_depth_m=5000.0, volume_change_m3=1e7)
    assert mogi["vertical_displacement_m"] > 0.0

    plume_h = VolcanicPhysicsEngine.volcanic_plume_height_km(volumetric_eruption_rate_m3_s=1e5)
    assert plume_h > 15.0  # km


def test_tsunami_forecast_engine():
    """Test de la célérité de tsunami C = sqrt(g*d), loi de Green et alerte tsunami."""
    c_ms = TsunamiForecastEngine.tsunami_wave_celerity_m_s(water_depth_m=4000.0)
    assert c_ms > 190.0  # ~198 m/s (~712 km/h)

    green_h = TsunamiForecastEngine.greens_law_coastal_amplification(h1_open_ocean_m=0.5, d1_open_ocean_m=4000.0, d2_coastal_depth_m=10.0)
    assert green_h > 2.0  # m

    tsunami_haz = TsunamiForecastEngine().evaluate_tsunami_hazard(earthquake_mw=8.5, fault_depth_km=15.0, distance_to_coast_km=200.0)
    assert tsunami_haz["warning_level"] == "RED / TSUNAMI WARNING"


def test_slope_stability_and_landslides():
    """Test du Facteur de Sécurité FS et de l'évaluation du risque de glissement de terrain."""
    fs = SlopeStabilityEngine.factor_of_safety(cohesion_kpa=10.0, normal_stress_kpa=100.0, pore_water_pressure_kpa=20.0, friction_angle_deg=30.0, shear_stress_kpa=50.0)
    assert fs > 1.0

    ls_risk = SlopeStabilityEngine.evaluate_landslide_trigger_risk(slope_angle_deg=35.0, rainfall_24h_mm=120.0, soil_saturation_pct=95.0)
    assert "CRITICAL" in ls_risk["landslide_risk"]


def test_geodesy_and_gravity():
    """Test du déplacement InSAR, vecteurs GNSS, pesanteur et anomalie de Bouguer."""
    insar_d = GeodesyEngine.insar_phase_to_displacement_mm(phase_shift_rad=3.14159)
    assert abs(insar_d - 13.87) < 0.5

    gnss = GeodesyEngine.gnss_displacement_vector("P001", ve_mm_yr=15.0, vn_mm_yr=20.0, vu_mm_yr=2.0)
    assert gnss["horizontal_velocity_mm_yr"] == 25.0

    bouguer = GravityEngine.bouguer_gravity_anomaly_mgal(observed_g_mgal=980000.0, latitude_deg=45.0, elevation_m=500.0)
    assert "bouguer_anomaly_mgal" in bouguer


def test_solid_earth_geomagnetism():
    """Test du champ dipolaire magnétique terrestre (IGRF / WMM)."""
    mag = SolidEarthGeomagneticEngine.calculate_dipole_field(latitude_deg=45.0)
    assert mag["total_intensity_nt"] > 40000.0


def test_multi_hazard_engine():
    """Test de l'évaluation combinée des risques géologiques."""
    haz = HazardEngine.evaluate_multi_hazard_risk(earthquake_mw=7.8, coastal_distance_km=20.0, slope_angle_deg=30.0)
    assert len(haz["identified_geological_hazards"]) >= 3
    assert "CRITICAL" in haz["multi_hazard_severity"]


def test_geological_observatories_and_dashboard():
    """Test du registre des observatoires (USGS, EMSC) et des métadonnées AWCI GEOLOGY CENTER."""
    assert len(GEOLOGICAL_OBSERVATORIES_REGISTRY) >= 3
    usgs = GeologicalObservatoryEngine.get_observatory("usgs")
    assert usgs is not None
    assert "Reston" in usgs.location

    dash = GeologyCenterDashboard.get_dashboard_metadata()
    assert dash["workspace_name"] == "GEOLOGY CENTER"


def test_geology_ai_and_query_engine():
    """Test de l'IA explicative et des requêtes du ScientificQueryEngine."""
    ai_eq = GeologicalReasoningEngine.explain_earthquake_physics()
    assert "Rebound" in ai_eq["phenomenon"]

    q_engine = ScientificQueryEngine()

    r1 = q_engine.ask("Show earthquakes")
    assert r1["layer_type"] == "earthquake_catalog_layer"

    r2 = q_engine.ask("Show volcanoes")
    assert r2["layer_type"] == "volcano_monitoring_layer"

    r3 = q_engine.ask("Show tsunami")
    assert r3["layer_type"] == "tsunami_propagation_layer"

    r4 = q_engine.ask("Explain Mw")
    assert "M_0" in r4["equation"]

    r5 = q_engine.ask("Explain Gutenberg Richter")
    assert "log_{10}" in r5["equation"]
