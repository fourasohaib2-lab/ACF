"""
Tests for acf.science.wind_turbulence.
"""

import pytest

from acf.science.wind_turbulence import CATIndex, JetStream, TKEProduction


def test_vertical_wind_shear():
    vws = CATIndex.vertical_wind_shear(du_dz=0.003, dv_dz=0.004)
    assert vws == pytest.approx(0.005)


def test_deformation_zero_when_no_deformation():
    d = CATIndex.deformation(du_dx=0.0, dv_dy=0.0, dv_dx=0.0, du_dy=0.0)
    assert d == 0.0


def test_convergence_sign():
    # Convergent flow (du/dx + dv/dy < 0) should give positive CVG.
    cvg = CATIndex.convergence(du_dx=-0.001, dv_dy=-0.001)
    assert cvg == pytest.approx(0.002)


def test_ti1_product_of_shear_and_deformation():
    vws = CATIndex.vertical_wind_shear(0.003, 0.004)
    deform = CATIndex.deformation(0.001, -0.001, 0.0005, 0.0005)
    ti1 = CATIndex.ti1(vws, deform)
    assert ti1 == pytest.approx(vws * deform)


def test_ti2_matches_ellrod_formula():
    vws = 0.005
    deform = 0.002
    cvg = 0.0015
    ti2 = CATIndex.ti2(vws, deform, cvg)
    assert ti2 == pytest.approx(vws * (deform + cvg))


def test_category_thresholds():
    assert CATIndex.category(2e-7) == "Smooth to Light"
    assert CATIndex.category(5e-7) == "Light-Moderate"
    assert CATIndex.category(9e-7) == "Moderate"
    assert CATIndex.category(15e-7) == "Moderate-Severe"


def test_jet_stream_threshold():
    assert JetStream.is_jet_stream(29.9) is False
    assert JetStream.is_jet_stream(30.0) is True
    assert JetStream.is_jet_stream(50.0) is True


def test_tke_mechanical_production_nonnegative():
    p = TKEProduction.mechanical_production(eddy_viscosity_km=5.0, du_dz=0.01, dv_dz=0.01)
    assert p >= 0
    assert p == pytest.approx(5.0 * (0.01**2 + 0.01**2))


def test_tke_mechanical_production_invalid_negative_km():
    with pytest.raises(ValueError):
        TKEProduction.mechanical_production(eddy_viscosity_km=-1.0, du_dz=0.01, dv_dz=0.01)


def test_tke_buoyancy_production_positive_when_unstable():
    # Unstable: dtheta/dz < 0 -> production should be positive (source).
    p = TKEProduction.buoyancy_production(eddy_diffusivity_kh=5.0, potential_temperature_k=300.0, dtheta_dz=-0.01)
    assert p > 0


def test_tke_buoyancy_production_negative_when_stable():
    # Stable: dtheta/dz > 0 -> production should be negative (sink, suppresses turbulence).
    p = TKEProduction.buoyancy_production(eddy_diffusivity_kh=5.0, potential_temperature_k=300.0, dtheta_dz=0.01)
    assert p < 0


def test_tke_buoyancy_production_invalid_temperature():
    with pytest.raises(ValueError):
        TKEProduction.buoyancy_production(eddy_diffusivity_kh=5.0, potential_temperature_k=0.0, dtheta_dz=0.01)
