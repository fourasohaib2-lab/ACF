"""
Tests for ACF-021 Complete Atmospheric Scientific Encyclopedia Expansion
"""

import pytest
from acf.science import EncyclopediaRegistry, KnowledgeGraphEngine
from acf.science.encyclopedia.cloud_microphysics import WMOCloudClassifier
from acf.science.physics_ai import PhysicsInformedAIArchitectures, ScientificReasoningEngine
from acf.science.encyclopedia.knowledge_sources import KnowledgeSourcesIndexer


def test_expanded_encyclopedia_entries_count():
    count = EncyclopediaRegistry.count()
    assert count >= 35


def test_wmo_cloud_classifier():
    classifier = WMOCloudClassifier()
    genre = classifier.classify_genre(base_m=1000.0, temp_c=-10.0, vertical_extension_m=10000.0)
    assert "Cumulonimbus" in genre


def test_stp_index_calculation():
    stp = EncyclopediaRegistry.calculate("stp_index_tornado", cape=3000.0, srh1km=300.0, lcl_m=800.0, shear6km=25.0)
    assert stp > 1.0


def test_lightning_flash_rate_calculation():
    rate = EncyclopediaRegistry.calculate("lightning_flash_rate_price_rind", cloud_top_height_km=14.0)
    assert rate > 10.0


def test_storm_relative_helicity_calculation():
    srh = EncyclopediaRegistry.calculate("storm_relative_helicity_srh", u_shear=15.0, v_shear=20.0, storm_u=10.0, storm_v=15.0)
    assert srh != 0.0


def test_tke_and_richardson_calculation():
    ri = EncyclopediaRegistry.calculate("richardson_number_gradient", g_over_theta=0.033, dtheta_dz=0.005, du_dz=0.02)
    assert ri > 0.0


def test_sensible_heat_flux_calculation():
    h = EncyclopediaRegistry.calculate("sensible_heat_flux_bulk", rho=1.2, cp=1004.0, U10=10.0, dt=5.0)
    assert h > 0.0


def test_physics_ai_reasoning_engine():
    engine = ScientificReasoningEngine()
    res = engine.explain_forecast_chain({"cape": 2500.0, "rh": 85.0})
    assert "CAPE élevé" in res["explanation"]
    assert "Foudre & Electrification" in res["explanation"]


def test_pinn_loss_and_knowledge_sources():
    pinn_loss = PhysicsInformedAIArchitectures.pinn_loss_formulation(data_loss=0.01, pde_residual_loss=0.005)
    assert pinn_loss == 0.015

    sources = KnowledgeSourcesIndexer.search_sources("WMO")
    assert len(sources) >= 2
