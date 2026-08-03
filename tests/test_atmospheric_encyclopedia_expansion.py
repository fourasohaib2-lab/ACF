"""
Tests for MISSION ACF-021 Complete Atmospheric Scientific Encyclopedia Expansion
"""

import pytest
import numpy as np
from acf.science import EncyclopediaRegistry, KnowledgeGraphEngine
from acf.science.encyclopedia.cloud_microphysics import WMOCloudClassifier
from acf.science.physics_ai import PhysicsInformedAIArchitectures, ScientificReasoningEngine
from acf.science.encyclopedia.knowledge_sources import KnowledgeSourcesIndexer


def test_expanded_encyclopedia_entries_count():
    count = EncyclopediaRegistry.count()
    assert count >= 60, f"Expected at least 60 entries, found {count}"


def test_wmo_cloud_classifier():
    classifier = WMOCloudClassifier()
    cb = classifier.classify_genre(base_m=1000.0, temp_c=-10.0, vertical_extension_m=10000.0)
    assert "Cumulonimbus" in cb
    ns = classifier.classify_genre(base_m=1000.0, temp_c=5.0, vertical_extension_m=4000.0)
    assert "Nimbostratus" in ns
    ci = classifier.classify_genre(base_m=7000.0, temp_c=-40.0, vertical_extension_m=500.0)
    assert "Cirrus" in ci


def test_cloud_microphysics_calculations():
    # LCL
    lcl = EncyclopediaRegistry.calculate("lcl_height_equation", temp_c=25.0, dewpoint_c=15.0)
    assert lcl == 1250.0

    # Bergeron-Findeisen
    delta_e = EncyclopediaRegistry.calculate("bergeron_findeisen_process", temp_c=-15.0)
    assert delta_e > 0.0

    # Kessler autoconversion
    dqr_dt = EncyclopediaRegistry.calculate("kessler_autoconversion_process", qc=0.002, qc0=0.001)
    assert dqr_dt > 0.0


def test_nwp_microphysics_schemes():
    thompson = EncyclopediaRegistry.get("wrf_thompson_scheme")
    assert thompson is not None
    assert "NCAR" in thompson.references[0] or "Thompson" in thompson.references[0]

    ice4 = EncyclopediaRegistry.get("arome_ice4_scheme")
    assert ice4 is not None
    assert "grêle" in ice4.description.lower() or "qh" in ice4.equation

    ifs_cloud = EncyclopediaRegistry.get("ecmwf_ifs_cloud_scheme")
    assert ifs_cloud is not None

    seifert = EncyclopediaRegistry.get("icon_seifert_beheng")
    assert seifert is not None


def test_convective_indices_and_calculations():
    # CAPE & CIN
    tv_p = [300.0, 298.0, 295.0, 290.0]
    tv_e = [298.0, 295.0, 294.0, 292.0]
    cape = EncyclopediaRegistry.calculate("cape_convective_energy", tv_parcel=tv_p, tv_env=tv_e, dz=100.0)
    assert cape > 0.0

    cin = EncyclopediaRegistry.calculate("cin_convective_inhibition", tv_parcel=tv_p, tv_env=tv_e, dz=100.0)
    assert cin >= 0.0

    # Lifted Index
    li = EncyclopediaRegistry.calculate("lifted_index_li", t_env_500_c=-15.0, t_parcel_500_c=-10.0)
    assert li == -5.0

    # K Index
    ki = EncyclopediaRegistry.calculate("k_index_ki", t850_c=18.0, t500_c=-12.0, td850_c=14.0, t700_c=8.0, td700_c=4.0)
    assert ki == (18.0 - (-12.0)) + 14.0 - (8.0 - 4.0)

    # STP
    stp = EncyclopediaRegistry.calculate("stp_index_tornado", cape=3000.0, srh1km=300.0, lcl_m=800.0, shear6km=25.0)
    assert stp > 1.0

    # SCP
    scp = EncyclopediaRegistry.calculate("scp_supercell_composite", cape=2000.0, srh3km=200.0, bwd6km=25.0)
    assert scp > 1.0


def test_lightning_and_tles():
    rate_land = EncyclopediaRegistry.calculate("lightning_flash_rate_price_rind", cloud_top_height_km=14.0, is_marine=False)
    assert rate_land > 10.0

    rate_sea = EncyclopediaRegistry.calculate("lightning_flash_rate_price_rind", cloud_top_height_km=14.0, is_marine=True)
    assert rate_sea < rate_land

    sprite = EncyclopediaRegistry.get("sprites_tles_mesosphere")
    assert sprite is not None
    assert "Mésosphère" in sprite.domain or "Mésosphère" in sprite.equation or "Mésosphère" in sprite.subdomain or "Mésosphère" in sprite.description


def test_severe_weather_and_srh():
    u_prof = [0.0, 5.0, 10.0, 15.0, 20.0]
    v_prof = [0.0, 5.0, 10.0, 15.0, 20.0]
    srh = EncyclopediaRegistry.calculate("storm_relative_helicity_srh", u_profile=u_prof, v_profile=v_prof, storm_u=5.0, storm_v=5.0, dz=500.0)
    assert isinstance(srh, float)

    mesh_desc = EncyclopediaRegistry.calculate("hail_size_estimation_mesh", mesh_mm=55.0)
    assert "tennis" in mesh_desc.lower() or "grosse grêle" in mesh_desc.lower()


def test_turbulence_and_richardson():
    e_k = EncyclopediaRegistry.calculate("kolmogorov_5_3_spectrum", k=0.1, epsilon=0.01)
    assert e_k > 0.0

    ri = EncyclopediaRegistry.calculate("richardson_number_gradient", g_over_theta=0.033, dtheta_dz=0.005, du_dz=0.02)
    assert ri > 0.0

    edr = EncyclopediaRegistry.calculate("aviation_edr_turbulence", epsilon=0.064)
    assert pytest.approx(edr, 0.01) == 0.4


def test_ocean_atmosphere_fluxes():
    h = EncyclopediaRegistry.calculate("sensible_heat_flux_bulk", rho=1.2, cp=1004.0, u10=10.0, ts_k=295.0, ta_k=290.0)
    assert h > 0.0

    le = EncyclopediaRegistry.calculate("latent_heat_flux_bulk", rho=1.2, lv=2.5e6, u10=10.0, qs=0.015, qa=0.010)
    assert le > 0.0

    nao = EncyclopediaRegistry.calculate("north_atlantic_oscillation_nao", slp_azores_hpa=1025.0, slp_iceland_hpa=990.0)
    assert nao > 0.0


def test_chemistry_and_aerosols():
    o3 = EncyclopediaRegistry.get("chapman_stratospheric_cycle")
    assert o3 is not None
    assert "Ozone" in o3.name

    dust = EncyclopediaRegistry.get("mineral_dust_aerosol")
    assert dust is not None


def test_satellite_and_radar():
    # Radar Z-R
    z = EncyclopediaRegistry.calculate("radar_reflectivity_z_r_relation", r_mm_h=10.0)
    assert z > 0.0

    r = EncyclopediaRegistry.calculate("qpe_quantitative_precipitation_estimation", z_dbz=40.0)
    assert r > 0.0

    # Satellite CTT
    ctt = EncyclopediaRegistry.get("cloud_top_temperature_retrieval")
    assert ctt is not None


def test_nwp_models_documentation():
    ifs = EncyclopediaRegistry.get("nwp_ecmwf_ifs_specifications")
    assert ifs is not None
    assert "TCo1279" in ifs.variables.get("Résolution", "")

    arome = EncyclopediaRegistry.get("nwp_meteo_france_arome_specifications")
    assert arome is not None
    assert "1.3 km" in arome.variables.get("Résolution", "")

    wrf = EncyclopediaRegistry.get("nwp_wrf_arw_specifications")
    assert wrf is not None

    icon = EncyclopediaRegistry.get("nwp_dwd_icon_specifications")
    assert icon is not None


def test_data_assimilation_and_mathematics():
    # 3D-Var Cost function
    x = [1.0, 2.0]
    xb = [0.0, 0.0]
    b_inv = [[1.0, 0.0], [0.0, 1.0]]
    y = [3.0]
    hx = [2.0]
    r_inv = [[1.0]]

    j_val = EncyclopediaRegistry.calculate("cost_function_variational_assimilation", x=x, xb=xb, b_inv=b_inv, y=y, hx=hx, r_inv=r_inv)
    assert j_val == 3.0

    # Semi-Lagrangian departure point
    x_dep = EncyclopediaRegistry.calculate("semi_lagrangian_advection_scheme", x_arrival=10.0, u_arrival=2.0, dt=1.0)
    assert x_dep == 8.0


def test_physics_ai_reasoning_engine():
    engine = ScientificReasoningEngine()
    res = engine.explain_forecast_chain({"cape": 2500.0, "rh": 85.0, "shear": 25.0})
    assert "CAPE élevé" in res["explanation"]
    assert "Cumulonimbus" in res["explanation"]
    assert "foudre" in res["explanation"]
    assert "fortes pluies" in res["explanation"]
    assert "grêle & supercellule" in res["explanation"]

    pinn_loss = PhysicsInformedAIArchitectures.pinn_loss_formulation(data_loss=0.01, pde_residual_loss=0.005)
    assert pinn_loss == 0.015

    fno_specs = PhysicsInformedAIArchitectures.fourier_neural_operator_specs()
    assert fno_specs["resolution_invariant"] is True

    gnn_specs = PhysicsInformedAIArchitectures.graph_neural_network_weather_specs()
    assert "GraphCast" in gnn_specs["name"]


def test_knowledge_sources_indexer():
    sources = KnowledgeSourcesIndexer.search_sources("WMO")
    assert len(sources) >= 3

    ecmwf_sources = KnowledgeSourcesIndexer.search_sources("ECMWF")
    assert len(ecmwf_sources) >= 1

    noaa_sources = KnowledgeSourcesIndexer.search_sources("NOAA")
    assert len(noaa_sources) >= 1
