"""
Tests for acf.science.synoptic.
"""

import pytest

from acf.science.synoptic import Coriolis, ErtelPotentialVorticity, GeostrophicWind, ThermalWind


def test_coriolis_at_equator_is_zero():
    assert Coriolis.parameter(0.0) == pytest.approx(0.0, abs=1e-12)


def test_coriolis_at_45n_known_value():
    # Standard textbook value: f ~ 1.03e-4 s^-1 at 45 deg latitude.
    assert Coriolis.parameter(45.0) == pytest.approx(1.031e-4, rel=1e-2)


def test_coriolis_opposite_sign_in_southern_hemisphere():
    assert Coriolis.parameter(-45.0) == pytest.approx(-Coriolis.parameter(45.0))


def test_coriolis_invalid_latitude():
    with pytest.raises(ValueError):
        Coriolis.parameter(100.0)


def test_beta_parameter_at_45n_known_value():
    # Standard beta-plane reference value: beta0 ~ 1.6e-11 m^-1 s^-1 at 45N.
    assert Coriolis.beta_parameter(45.0) == pytest.approx(1.6e-11, rel=0.05)


def test_beta_parameter_max_at_equator():
    assert Coriolis.beta_parameter(0.0) > Coriolis.beta_parameter(45.0)


def test_geostrophic_wind_matches_registered_law_formula():
    ug, vg = GeostrophicWind.calculate(dp_dx=0.01, dp_dy=0.02, density=1.2, coriolis_f=1e-4)
    assert ug == pytest.approx(-0.02 / (1e-4 * 1.2))
    assert vg == pytest.approx(0.01 / (1e-4 * 1.2))


def test_geostrophic_wind_invalid_zero_coriolis():
    with pytest.raises(ValueError):
        GeostrophicWind.calculate(dp_dx=0.01, dp_dy=0.02, density=1.2, coriolis_f=0.0)


def test_thermal_wind_zero_gradient_gives_zero_shear():
    dug, dvg = ThermalWind.calculate(dt_dx=0.0, dt_dy=0.0, coriolis_f=1e-4, mean_temperature_k=280.0)
    assert dug == pytest.approx(0.0)
    assert dvg == pytest.approx(0.0)


def test_thermal_wind_known_formula():
    dug, dvg = ThermalWind.calculate(dt_dx=1e-5, dt_dy=2e-5, coriolis_f=1e-4, mean_temperature_k=280.0)
    from acf.science.constants import RD

    assert dug == pytest.approx((RD / 1e-4) * 2e-5)
    assert dvg == pytest.approx(-(RD / 1e-4) * 1e-5)


def test_thermal_wind_invalid_zero_coriolis():
    with pytest.raises(ValueError):
        ThermalWind.calculate(dt_dx=1e-5, dt_dy=1e-5, coriolis_f=0.0, mean_temperature_k=280.0)


def test_ertel_pv_matches_underlying_module():
    from acf.science.potential_vorticity import PotentialVorticity

    assert ErtelPotentialVorticity.calculate(2e-5, 1e-4, -0.002) == PotentialVorticity.calculate(
        2e-5, 1e-4, -0.002
    )
