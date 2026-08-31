"""
Atmospheric Complexity Framework (ACF)

MODEL4D - Cloud Radiative Feedback Test Suite

This file was previously empty - pytest collected it but ran no tests,
so the real source module (src/acf/model4d/physics/
cloud_radiative_feedback.py) had 0% coverage and was never actually
verified. Added real tests exercising the actual source class.
"""

import pytest

from acf.model4d.physics.cloud_radiative_feedback import CloudRadiativeFeedback


def test_cloud_optical_thickness_matches_formula():
    lwp, r_eff = 150.0, 10.0
    result = CloudRadiativeFeedback.cloud_optical_thickness(lwp, r_eff)
    assert result == pytest.approx(1.5 * (lwp / r_eff))


def test_cloud_optical_thickness_rejects_invalid_inputs():
    with pytest.raises(ValueError):
        CloudRadiativeFeedback.cloud_optical_thickness(100.0, 0.0)
    with pytest.raises(ValueError):
        CloudRadiativeFeedback.cloud_optical_thickness(-1.0, 10.0)


def test_shortwave_cloud_forcing_is_cooling():
    # Higher cloud albedo than surface -> net cooling (negative forcing)
    result = CloudRadiativeFeedback.shortwave_cloud_forcing(solar_irradiance=1000.0, cloud_albedo=0.6)
    assert result < 0.0
    assert result == pytest.approx(-1000.0 * (0.6 - 0.15))


def test_shortwave_cloud_forcing_clamped_when_albedo_below_surface():
    result = CloudRadiativeFeedback.shortwave_cloud_forcing(solar_irradiance=1000.0, cloud_albedo=0.05)
    assert result == 0.0


def test_longwave_cloud_forcing_scales_with_cloud_fraction():
    full = CloudRadiativeFeedback.longwave_cloud_forcing(surface_emission=400.0, cloud_top_emission=250.0)
    half = CloudRadiativeFeedback.longwave_cloud_forcing(
        surface_emission=400.0, cloud_top_emission=250.0, cloud_fraction=0.5
    )
    assert full == pytest.approx(150.0)
    assert half == pytest.approx(75.0)


def test_longwave_cloud_forcing_rejects_invalid_fraction():
    with pytest.raises(ValueError):
        CloudRadiativeFeedback.longwave_cloud_forcing(400.0, 250.0, cloud_fraction=1.5)


def test_net_cloud_radiative_forcing():
    result = CloudRadiativeFeedback.net_cloud_radiative_forcing(sw_forcing=-50.0, lw_forcing=20.0)
    assert result == pytest.approx(-30.0)
