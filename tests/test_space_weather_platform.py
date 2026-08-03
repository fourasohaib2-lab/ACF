"""
Atmospheric Complexity Framework (ACF)

Global Operational Space Weather, Space Environment & Heliophysics Test Suite (MISSION ACF-034)
"""

from acf.space_weather.solar.solar_database import SolarDatabase, SolarFlareEngine, CoronalMassEjectionInfo
from acf.space_weather.solar_wind.solar_wind_engine import SolarWindEngine, InterplanetaryMagneticField
from acf.space_weather.geomagnetism.geomagnetic_engine import GeomagneticEngine, GeomagneticStormScale
from acf.space_weather.ionosphere.ionosphere_engine import IonosphereEngine, RadioBlackoutScale
from acf.space_weather.magnetosphere.radiation_belts import RadiationBeltsEngine
from acf.space_weather.satellites.spacecraft_effects import SatelliteImpactEngine, SATELLITE_REGISTRY
from acf.space_weather.aviation.aviation_space_weather import AviationSpaceWeatherEngine
from acf.space_weather.models.space_models import SpaceWeatherModelEngine, SPACE_WEATHER_MODELS_REGISTRY
from acf.space_weather.observations.observatories import SpaceObservatoryEngine, SPACE_OBSERVATORIES_REGISTRY
from acf.space_weather.forecast.forecast_engine import SpaceWeatherForecastEngine
from acf.space_weather.alerts.space_alerts import SpaceWeatherAlertEngine
from acf.science.query_engine import ScientificQueryEngine


def test_solar_physics_and_flares():
    """Test du nombre de Wolf, des éruptions GOES (X-ray) et des CMEs."""
    r = SolarDatabase.wolf_sunspot_number(num_groups=12, num_spots=35)
    assert r == 155.0

    flare_x = SolarFlareEngine.classify_goes_xray_flare(xray_flux_w_m2=5.8e-4)
    assert flare_x["flare_class"] == "X5.8"
    assert "Extreme" in flare_x["severity"]

    cme = CoronalMassEjectionInfo(
        cme_id="CME-01",
        active_region="AR13664",
        speed_km_s=1500.0,
        angular_width_deg=360.0,
        is_halo_cme=True,
        direction_earth_directed=True,
        estimated_arrival_earth_hours=28.0,
    )
    assert cme.is_halo_cme is True


def test_solar_wind_and_imf():
    """Test de la pression dynamique, de l'angle d'horloge de l'IMF et de la spirale de Parker."""
    pdyn = SolarWindEngine.dynamic_pressure_npa(solar_wind_speed_km_s=600.0, proton_density_cm3=10.0)
    assert pdyn > 1.0

    imf = InterplanetaryMagneticField(bx_nt=2.0, by_nt=-5.0, bz_nt=-12.0, total_b_nt=13.2)
    assert imf.clock_angle_deg > 180.0

    risk = SolarWindEngine.evaluate_reconnection_risk(imf)
    assert "CRITICAL" in risk["reconnection_risk"]


def test_geomagnetic_engine_and_noaa_scales():
    """Test de la distance de magnétopause Rmp, des indices Dst/Kp et de l'échelle G1-G5."""
    g5 = GeomagneticStormScale.classify_kp_index(kp_value=9.0)
    assert "G5" in g5["noaa_scale"]

    rmp = GeomagneticEngine.magnetopause_standoff_distance_re(pdyn_npa=12.0, bz_nt=-10.0)
    assert 4.0 < rmp < 9.0

    dst = GeomagneticEngine.evaluate_dst_index_severity(dst_nt=-150.0)
    assert "Intense" in dst["severity"]


def test_ionosphere_and_radio_blackouts():
    """Test du retard de groupe GNSS/GPS, MUF et de l'échelle NOAA Radio Blackout R1-R5."""
    r3 = RadioBlackoutScale.classify_xray_radio_blackout(xray_flux_w_m2=1.5e-4)
    assert "R3" in r3["radio_blackout_scale"]

    delay_m = IonosphereEngine.gnss_range_delay_meters(tec_tecu=50.0)
    assert delay_m > 5.0

    muf = IonosphereEngine.maximum_usable_frequency_muf_mhz(fof2_mhz=10.0)
    assert muf == 30.0


def test_radiation_belts_and_satellites():
    """Test des ceintures de Van Allen, du freinage atmosphérique LEO et du registre satellite."""
    belt = RadiationBeltsEngine.evaluate_van_allen_belt_flux(altitude_km=20000.0, electron_flux_gt_2mev=5e4)
    assert "Outer" in belt["van_allen_zone"]
    assert "HIGH" in belt["charging_hazard_risk"]

    assert len(SATELLITE_REGISTRY) >= 3
    drag = SatelliteImpactEngine.calculate_leo_drag_increase(f107_index=170.0)
    assert drag > 1.0


def test_aviation_space_weather():
    """Test de la dose de radiation cosmique et des bulletins OACI SWX."""
    rad = AviationSpaceWeatherEngine.calculate_polar_flight_radiation_dose(flight_level=390, solar_proton_event_s_scale=2)
    assert rad["total_radiation_dose_usv_h"] > 30.0
    assert rad["risk_level"] == "HIGH"


def test_space_models_and_observatories():
    """Test du registre des modèles de temps spatial (WSA-ENLIL) et observatoires (DSCOVR)."""
    assert len(SPACE_WEATHER_MODELS_REGISTRY) >= 3
    enlil = SpaceWeatherModelEngine.get_model("wsa_enlil")
    assert enlil is not None
    assert "MHD" in enlil.governing_equations

    assert len(SPACE_OBSERVATORIES_REGISTRY) >= 2
    dscovr = SpaceObservatoryEngine.get_observatory("dscovr")
    assert dscovr is not None
    assert "L1" in dscovr.orbit_location


def test_space_weather_forecast_and_alerts():
    """Test du moteur de prévision et d'alerte météo-spatiale."""
    f_engine = SpaceWeatherForecastEngine()
    fcst = f_engine.generate_space_weather_forecast(sunspot_number=160.0, cme_speed_km_s=1400.0, imf_bz_nt=-15.0)
    assert fcst["predicted_max_kp_index"] >= 7.0

    alerts = SpaceWeatherAlertEngine.evaluate_system_alerts(kp_index=8.5, xray_flux_w_m2=2e-4, proton_flux_gt_10mev=2000.0)
    assert len(alerts) >= 3


def test_query_engine_phase18_space_weather_questions():
    """Test du ScientificQueryEngine sur les requêtes météo-spatiales de la mission ACF-034."""
    q_engine = ScientificQueryEngine()

    r1 = q_engine.ask("Show aurora")
    assert r1["layer_type"] == "auroral_oval_layer"

    r2 = q_engine.ask("Show Kp")
    assert r2["widget_type"] == "GeomagneticIndicesViewer"

    r3 = q_engine.ask("Show solar wind")
    assert r3["layer_type"] == "solar_wind_streamlines"

    r4 = q_engine.ask("Show TEC")
    assert r4["layer_type"] == "ionospheric_tec_layer"

    r5 = q_engine.ask("Explain Van Allen belts")
    assert "Inner Belt" in r5["van_allen_belts"][0]

    r6 = q_engine.ask("Explain solar flare")
    assert "X-Class" in r6["goes_classes"][2]
