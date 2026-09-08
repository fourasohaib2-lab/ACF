"""
Tests for acf.science.boundary_layer.
"""

import math

import pytest

from acf.science.boundary_layer import BowenRatio, FrictionVelocity, MoninObukhovLength, PBLHeight


def test_monin_obukhov_length_unstable_is_negative():
    L = MoninObukhovLength.calculate(friction_velocity=0.3, virtual_temperature_k=300.0, kinematic_heat_flux=0.2)
    assert L < 0


def test_monin_obukhov_length_stable_is_positive():
    L = MoninObukhovLength.calculate(friction_velocity=0.3, virtual_temperature_k=300.0, kinematic_heat_flux=-0.05)
    assert L > 0


def test_monin_obukhov_length_neutral_is_infinite():
    L = MoninObukhovLength.calculate(friction_velocity=0.3, virtual_temperature_k=300.0, kinematic_heat_flux=0.0)
    assert math.isinf(L)


def test_monin_obukhov_length_invalid_ustar():
    with pytest.raises(ValueError):
        MoninObukhovLength.calculate(friction_velocity=0.0, virtual_temperature_k=300.0, kinematic_heat_flux=0.1)


def test_stability_regime():
    assert MoninObukhovLength.stability_regime(-50.0, 10.0) == "Unstable"
    assert MoninObukhovLength.stability_regime(50.0, 10.0) == "Stable"
    assert MoninObukhovLength.stability_regime(math.inf, 10.0) == "Neutral"


def test_friction_velocity_positive():
    ustar = FrictionVelocity.calculate(wind_speed=5.0, height_m=10.0, roughness_length_m=0.03)
    assert ustar > 0


def test_friction_velocity_invalid_height_below_roughness():
    with pytest.raises(ValueError):
        FrictionVelocity.calculate(wind_speed=5.0, height_m=0.01, roughness_length_m=0.03)


def test_friction_velocity_matches_log_law_inversion():
    # u* from FrictionVelocity should reproduce U(z) via the log law.
    ustar = FrictionVelocity.calculate(wind_speed=6.0, height_m=10.0, roughness_length_m=0.1)
    u_reconstructed = (ustar / 0.40) * math.log(10.0 / 0.1)
    assert u_reconstructed == pytest.approx(6.0)


def test_bowen_ratio_known_case():
    # gamma = Cp*p/(epsilon*Lv); sanity: positive dT, positive de -> positive beta
    beta = BowenRatio.calculate(delta_temperature_k=2.0, delta_vapor_pressure_hpa=1.0, pressure_hpa=1000.0)
    assert beta > 0


def test_bowen_ratio_zero_delta_e_raises():
    with pytest.raises(ValueError):
        BowenRatio.calculate(delta_temperature_k=2.0, delta_vapor_pressure_hpa=0.0, pressure_hpa=1000.0)


def test_bowen_ratio_partition_fluxes_sum_to_available_energy():
    beta = 0.5
    fluxes = BowenRatio.partition_fluxes(net_radiation_w_m2=500.0, soil_heat_flux_w_m2=50.0, bowen_ratio=beta)
    total = fluxes["sensible_heat_flux_w_m2"] + fluxes["latent_heat_flux_w_m2"]
    assert total == pytest.approx(500.0 - 50.0)
    assert fluxes["sensible_heat_flux_w_m2"] == pytest.approx(beta * fluxes["latent_heat_flux_w_m2"])


def test_bowen_ratio_partition_fluxes_invalid_minus_one():
    with pytest.raises(ValueError):
        BowenRatio.partition_fluxes(net_radiation_w_m2=500.0, soil_heat_flux_w_m2=50.0, bowen_ratio=-1.0)


def test_pbl_height_parcel_method_interpolates():
    heights = [0.0, 500.0, 1000.0, 1500.0, 2000.0]
    theta = [300.0, 301.0, 303.0, 306.0, 310.0]
    zi = PBLHeight.parcel_method(heights, theta, surface_potential_temperature_k=302.0)
    # threshold 302 is between theta[1]=301 (z=500) and theta[2]=303 (z=1000)
    assert 500.0 < zi < 1000.0


def test_pbl_height_parcel_method_with_excess():
    heights = [0.0, 500.0, 1000.0]
    theta = [300.0, 302.0, 305.0]
    zi_no_excess = PBLHeight.parcel_method(heights, theta, surface_potential_temperature_k=300.0, excess_k=0.0)
    zi_with_excess = PBLHeight.parcel_method(heights, theta, surface_potential_temperature_k=300.0, excess_k=2.0)
    assert zi_with_excess > zi_no_excess


def test_pbl_height_parcel_method_never_reached_returns_top():
    heights = [0.0, 500.0, 1000.0]
    theta = [300.0, 301.0, 302.0]
    zi = PBLHeight.parcel_method(heights, theta, surface_potential_temperature_k=310.0)
    assert zi == 1000.0


def test_pbl_height_parcel_method_invalid_length_mismatch():
    with pytest.raises(ValueError):
        PBLHeight.parcel_method([0.0, 500.0], [300.0], surface_potential_temperature_k=300.0)
