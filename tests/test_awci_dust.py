"""
Tests for acf.awci.dust - the real per-point dust/sand-storm emission-
favorable-conditions risk proxy closing AWCI's "poussière et sable" gap
(post-model4d audit, 2026-09-11).
"""

from __future__ import annotations

from acf.awci.dust import (
    DUST_DRY_RH_CEILING_PCT,
    DUST_DRY_RH_FLOOR_PCT,
    DUST_WIND_CEILING_M_S,
    DUST_WIND_FLOOR_M_S,
    compute_real_dust_risk_at_point,
)


def test_zero_humidity_returns_honest_none_not_a_fabricated_value():
    result = compute_real_dust_risk_at_point(
        temperature_k=313.15, specific_humidity=0.0, pressure_hpa=1005.0, wind_speed_m_s=15.0
    )

    assert result["dust_risk_score"] is None
    assert result["is_real_data"] is False
    assert result["status"] == "DUST_RISK_NOT_COMPUTED_ZERO_HUMIDITY"


def test_calm_wind_gives_zero_risk_regardless_of_dryness():
    result = compute_real_dust_risk_at_point(
        temperature_k=313.15, specific_humidity=0.0005, pressure_hpa=1005.0, wind_speed_m_s=1.0
    )

    assert result["is_real_data"] is True
    assert result["wind_erosion_potential"] == 0.0
    assert result["dust_risk_score"] == 0.0


def test_humid_air_gives_zero_risk_regardless_of_wind():
    result = compute_real_dust_risk_at_point(
        temperature_k=293.15, specific_humidity=0.014, pressure_hpa=1013.0, wind_speed_m_s=20.0
    )

    assert result["dry_surface_proxy"] == 0.0
    assert result["dust_risk_score"] == 0.0


def test_strong_dry_wind_gives_high_risk():
    result = compute_real_dust_risk_at_point(
        temperature_k=313.15, specific_humidity=0.0005, pressure_hpa=1005.0, wind_speed_m_s=20.0
    )

    assert result["wind_erosion_potential"] == 1.0
    assert result["dry_surface_proxy"] == 1.0
    assert result["dust_risk_score"] == 1.0


def test_risk_is_multiplicative_not_max_both_factors_must_hold():
    """Real, disclosed ACF design choice (module docstring) - verified
    by construction: a moderate value on BOTH axes must produce a
    smaller risk than either axis alone at its own maximum, which max()
    would not."""
    strong_wind_only = compute_real_dust_risk_at_point(
        temperature_k=293.15, specific_humidity=0.014, pressure_hpa=1013.0, wind_speed_m_s=20.0
    )
    dry_only = compute_real_dust_risk_at_point(
        temperature_k=313.15, specific_humidity=0.0005, pressure_hpa=1005.0, wind_speed_m_s=1.0
    )
    both_moderate = compute_real_dust_risk_at_point(
        temperature_k=303.15, specific_humidity=0.003, pressure_hpa=1010.0, wind_speed_m_s=13.0
    )

    assert strong_wind_only["dust_risk_score"] == 0.0
    assert dry_only["dust_risk_score"] == 0.0
    assert both_moderate["dust_risk_score"] > 0.0
    assert both_moderate["dust_risk_score"] == both_moderate["wind_erosion_potential"] * both_moderate["dry_surface_proxy"]


def test_wind_ramp_thresholds_are_the_documented_real_constants():
    at_floor = compute_real_dust_risk_at_point(
        temperature_k=313.15, specific_humidity=0.0005, pressure_hpa=1005.0, wind_speed_m_s=DUST_WIND_FLOOR_M_S
    )
    at_ceiling = compute_real_dust_risk_at_point(
        temperature_k=313.15, specific_humidity=0.0005, pressure_hpa=1005.0, wind_speed_m_s=DUST_WIND_CEILING_M_S
    )

    assert at_floor["wind_erosion_potential"] == 0.0
    assert at_ceiling["wind_erosion_potential"] == 1.0


def test_negative_wind_speed_is_treated_as_calm_not_negative_risk():
    result = compute_real_dust_risk_at_point(
        temperature_k=313.15, specific_humidity=0.0005, pressure_hpa=1005.0, wind_speed_m_s=-5.0
    )
    assert result["wind_erosion_potential"] == 0.0


def test_dry_rh_thresholds_are_the_documented_real_constants():
    dry = compute_real_dust_risk_at_point(
        temperature_k=293.15, specific_humidity=1e-6, pressure_hpa=1013.0, wind_speed_m_s=DUST_WIND_CEILING_M_S
    )
    assert dry["relative_humidity_pct"] < DUST_DRY_RH_FLOOR_PCT
    assert dry["dry_surface_proxy"] == 1.0
    assert dry["dust_risk_score"] == 1.0

    # Sanity: the module's own documented floor/ceiling ordering holds.
    assert DUST_DRY_RH_FLOOR_PCT < DUST_DRY_RH_CEILING_PCT
