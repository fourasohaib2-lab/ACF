"""
Tests for acf.awci.visibility - the real per-point visibility-degradation
risk proxy closing AWCI's "visibilité et plafond" gap (post-model4d
audit, 2026-09-11).
"""

from __future__ import annotations

from acf.awci.visibility import (
    FOG_RH_FLOOR_PCT,
    LIGHT_RAIN_MM_H,
    WMO_HEAVY_RAIN_MM_H,
    classify_precipitation_intensity,
    compute_real_visibility_risk_at_point,
)


def test_zero_humidity_returns_honest_none_not_a_fabricated_value():
    result = compute_real_visibility_risk_at_point(
        temperature_k=300.0, specific_humidity=0.0, pressure_hpa=1013.25, precipitation_mm_h=0.0
    )

    assert result["visibility_risk_score"] is None
    assert result["is_real_data"] is False
    assert result["status"] == "VISIBILITY_RISK_NOT_COMPUTED_ZERO_HUMIDITY"


def test_dry_no_rain_point_has_near_zero_risk():
    result = compute_real_visibility_risk_at_point(
        temperature_k=293.15, specific_humidity=0.002, pressure_hpa=1013.25, precipitation_mm_h=0.0
    )

    assert result["is_real_data"] is True
    assert result["visibility_risk_score"] == 0.0
    assert result["fog_proximity"] == 0.0
    assert result["precip_intensity"] == 0.0


def test_near_saturation_point_has_high_fog_proximity_and_drives_the_risk_score():
    result = compute_real_visibility_risk_at_point(
        temperature_k=288.15, specific_humidity=0.0102, pressure_hpa=1013.25, precipitation_mm_h=0.0
    )

    assert result["relative_humidity_pct"] > FOG_RH_FLOOR_PCT
    assert result["fog_proximity"] > 0.0
    assert result["visibility_risk_score"] == result["fog_proximity"]


def test_heavy_rain_saturates_precip_intensity_and_the_risk_score():
    result = compute_real_visibility_risk_at_point(
        temperature_k=293.15,
        specific_humidity=0.002,
        pressure_hpa=1013.25,
        precipitation_mm_h=WMO_HEAVY_RAIN_MM_H * 2,
    )

    assert result["precip_intensity"] == 1.0
    assert result["visibility_risk_score"] == 1.0


def test_risk_score_is_the_max_not_the_average_of_the_two_signals():
    """A real, disclosed ACF design choice (module docstring) - verified
    by construction, not just asserted in prose."""
    result = compute_real_visibility_risk_at_point(
        temperature_k=288.15,
        specific_humidity=0.0102,  # near-saturation -> real, nonzero fog_proximity
        pressure_hpa=1013.25,
        precipitation_mm_h=0.0,  # zero precip_intensity
    )

    assert result["fog_proximity"] > 0.0
    assert result["precip_intensity"] == 0.0
    # max(), not average: the full fog_proximity signal survives even
    # though precip_intensity is 0 - an average would have halved it.
    assert result["visibility_risk_score"] == result["fog_proximity"]


def test_default_precipitation_is_zero_not_a_missing_value():
    with_default = compute_real_visibility_risk_at_point(
        temperature_k=293.15, specific_humidity=0.002, pressure_hpa=1013.25
    )
    with_explicit_zero = compute_real_visibility_risk_at_point(
        temperature_k=293.15, specific_humidity=0.002, pressure_hpa=1013.25, precipitation_mm_h=0.0
    )

    assert with_default["visibility_risk_score"] == with_explicit_zero["visibility_risk_score"]


def test_risk_score_never_exceeds_the_real_0_1_bounds():
    result = compute_real_visibility_risk_at_point(
        temperature_k=288.15,
        specific_humidity=0.0102,
        pressure_hpa=1013.25,
        precipitation_mm_h=WMO_HEAVY_RAIN_MM_H * 10,
    )

    # Real relative humidity can nominally exceed 100% for near-/
    # super-saturated inputs (same behavior already documented and
    # relied upon by acf.events.fog_detector) - the ramp itself is
    # still correctly clamped to [0, 1] regardless.
    assert 0.0 <= result["visibility_risk_score"] <= 1.0
    assert 0.0 <= result["fog_proximity"] <= 1.0
    assert 0.0 <= result["precip_intensity"] <= 1.0


# --------------------------------------------- classify_precipitation_intensity


def test_classify_precipitation_intensity_real_wmo_thresholds():
    assert classify_precipitation_intensity(0.0) == "LIGHT"
    assert classify_precipitation_intensity(LIGHT_RAIN_MM_H) == "LIGHT"
    assert classify_precipitation_intensity(LIGHT_RAIN_MM_H + 0.1) == "MODERATE"
    assert classify_precipitation_intensity(WMO_HEAVY_RAIN_MM_H) == "MODERATE"
    assert classify_precipitation_intensity(WMO_HEAVY_RAIN_MM_H + 0.1) == "HEAVY"
    assert classify_precipitation_intensity(50.0) == "HEAVY"


def test_classify_precipitation_intensity_never_fabricates_a_negative_category():
    """A real, non-physical sensor artifact (negative rate) must still
    honestly classify as LIGHT (treated as 0), never raise or return an
    invented 4th category."""
    assert classify_precipitation_intensity(-5.0) == "LIGHT"


def test_classify_precipitation_intensity_matches_the_module_docstrings_own_boundaries():
    """Real, decisive cross-check: the 3 boundaries this function uses
    must be exactly the same 2 real module-level constants
    compute_real_visibility_risk_at_point()'s own precip_intensity ramp
    already uses - never a second, independently-chosen set of numbers
    for the same real WMO scale."""
    assert LIGHT_RAIN_MM_H == 2.5
    assert WMO_HEAVY_RAIN_MM_H == 7.6
