"""
Tests for ACF-020 Cloud Physics Knowledge Engine Complete Integration
"""

import pytest

from acf.ai.cloud_reasoning import CloudReasoningEngine
from acf.science.clouds import (
    CloudAerosolEngine,
    CloudClassificationEngine,
    CloudDataAssimilationEngine,
    CloudDynamicsEngine,
    CloudMicrophysicsEngine,
    CloudRadiationEngine,
    CloudScientificRegistry,
    CloudThermodynamicsEngine,
    SevereWeatherCloudModule,
)


def test_cloud_registry_lookup_and_calculate():
    proc = CloudScientificRegistry.get("kessler_autoconversion")
    assert proc is not None
    assert proc.name == "Schéma d'Autoconversion de Kessler"
    rate = CloudScientificRegistry.calculate("kessler_autoconversion", qc=0.001, qc_crit=0.0005)
    assert pytest.approx(rate, rel=1e-3) == 0.0005 * 0.001


def test_cloud_water_mass_conservation():
    micro = CloudMicrophysicsEngine()
    budget = micro.compute_budget(qv=0.015, qc=0.002, qr=0.0005, qi=0.0, qs=0.0, qg=0.0, dt=1.0)
    assert budget["mass_conserved"] is True
    assert budget["total_water"] == pytest.approx(0.0175, rel=1e-6)


def test_cloud_thermodynamics_lcl_cape():
    thermo = CloudThermodynamicsEngine()
    lcl = thermo.calculate_lcl(temp_k=298.15, dewpoint_k=288.15)
    assert pytest.approx(lcl, rel=1e-3) == 1250.0  # 125 * 10

    # CAPE calculation
    z_levels = [0.0, 1000.0, 2000.0, 3000.0]
    t_env = [298.15, 288.15, 278.15, 268.15]
    t_parcel = [298.15, 292.15, 284.15, 272.15]
    cape = thermo.calculate_cape(z_levels, t_env, t_parcel)
    assert cape > 0.0


def test_cloud_liquid_and_ice_water_content():
    micro = CloudMicrophysicsEngine()
    lwc = micro.liquid_water_content(qc=0.001, air_density=1.2)
    assert lwc == pytest.approx(0.0012, rel=1e-6)

    iwc = micro.ice_water_content(qi=0.0005, air_density=1.0)
    assert iwc == pytest.approx(0.0005, rel=1e-6)

    with pytest.raises(ValueError):
        micro.liquid_water_content(qc=-0.001)


def test_cloud_droplet_effective_radius_martin_1994():
    micro = CloudMicrophysicsEngine()
    # A denser, more polluted (higher N) cloud with the same LWC yields a
    # smaller effective radius — a basic physical sanity check.
    re_clean = micro.droplet_effective_radius(
        liquid_water_content_kg_m3=0.0005, droplet_number_concentration_m3=1e8, k=0.8
    )
    re_polluted = micro.droplet_effective_radius(
        liquid_water_content_kg_m3=0.0005, droplet_number_concentration_m3=1e9, k=0.8
    )
    assert re_clean > re_polluted > 0.0
    # Typical warm cloud droplets: a few to a few tens of micrometers.
    assert 1e-6 < re_clean < 100e-6

    with pytest.raises(ValueError):
        micro.droplet_effective_radius(liquid_water_content_kg_m3=0.0005, droplet_number_concentration_m3=0.0)


def test_cloud_microphysics_processes_registered():
    for key in ["liquid_water_content", "ice_water_content", "droplet_effective_radius"]:
        proc = CloudScientificRegistry.get(key)
        assert proc is not None


def test_cloud_dynamics_mass_flux():
    dyn = CloudDynamicsEngine()
    flux = dyn.mass_flux(density=1.2, updraft_w=10.0, area_fraction=0.05)
    assert pytest.approx(flux, rel=1e-3) == 0.6


def test_cloud_classification():
    classifier = CloudClassificationEngine()
    cb_result = classifier.classify(
        base_altitude_m=1000.0,
        top_altitude_m=12000.0,
        temperature_c=25.0,
        relative_humidity=0.85,
        cape_j_kg=2500.0,
        radar_reflectivity_dbz=55.0,
    )
    assert cb_result["genre"] == "Cumulonimbus"
    assert cb_result["family"] == "Convective"

    ci_result = classifier.classify(
        base_altitude_m=8000.0,
        top_altitude_m=9000.0,
        temperature_c=-40.0,
        relative_humidity=0.4,
        cloud_optical_depth=0.5,
    )
    assert ci_result["genre"] == "Cirrus"


def test_cloud_radiation_and_forcing():
    rad = CloudRadiationEngine()
    cod = rad.cloud_optical_depth(liquid_water_path_g_m2=100.0, effective_radius_um=10.0)
    assert cod > 0.0

    forcing = rad.cloud_radiative_forcing(
        solar_incident_w_m2=340.0,
        cloud_albedo_val=0.6,
        clear_sky_albedo=0.15,
    )
    assert forcing["SWCF_W_m2"] < 0.0


def test_cloud_aerosols():
    aero = CloudAerosolEngine()
    n_ccn = aero.twomey_ccn_activation(supersaturation_percent=1.0)
    assert n_ccn > 0.0


def test_severe_weather_cloud_module():
    severe = SevereWeatherCloudModule()
    li = severe.lifted_index(t_500_c=-15.0, t_parcel_500_c=-10.0)
    assert li == -5.0

    risk = severe.hail_risk_assessment(cape_j_kg=2500.0, freezing_level_m=3000.0, updraft_w_max=35.0)
    assert "Extrême" in risk["risk_level"]


def test_cloud_data_assimilation():
    da = CloudDataAssimilationEngine()
    res = da.assimilate_cloud_field(
        source="Meteosat",
        file_format="NetCDF",
        raw_field_data={"cloud_water": 0.001, "cloud_cover": 0.8},
    )
    assert res["status"] == "ASSIMILATED"


def test_cloud_ai_reasoning():
    reasoner = CloudReasoningEngine()
    explanation = reasoner.explain_cumulonimbus_formation(
        cape_j_kg=2500.0,
        surface_humidity_pct=80.0,
        low_level_convergence_s1=3e-5,
        shear_0_6km_m_s=25.0,
    )
    assert "Cumulonimbus" in explanation["question"]
    assert len(explanation["justification"]) >= 4
    assert len(explanation["physical_mechanisms"]) >= 4
