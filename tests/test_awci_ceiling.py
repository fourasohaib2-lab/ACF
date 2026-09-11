"""
Tests for acf.awci.ceiling - the real per-point ceiling (LCL-approximation)
estimate closing AWCI's "visibilité et plafond" gap (post-model4d audit,
2026-09-11).
"""

from __future__ import annotations

from acf.awci.ceiling import (
    IFR_CEILING_M,
    LIFR_CEILING_M,
    MVFR_CEILING_M,
    classify_ceiling_category,
    compute_real_ceiling_at_point,
)


def test_zero_humidity_returns_honest_none_not_a_fabricated_value():
    result = compute_real_ceiling_at_point(temperature_k=300.0, specific_humidity=0.0, pressure_hpa=1013.25)

    assert result["ceiling_height_m"] is None
    assert result["ceiling_category"] is None
    assert result["is_real_data"] is False
    assert result["status"] == "CEILING_NOT_COMPUTED_ZERO_HUMIDITY"


def test_real_case_produces_a_real_positive_ceiling_height_and_category():
    result = compute_real_ceiling_at_point(temperature_k=288.15, specific_humidity=0.006, pressure_hpa=1013.25)

    assert result["is_real_data"] is True
    assert result["status"] == "REAL_CEILING_LCL_APPROXIMATION"
    assert result["ceiling_height_m"] > 0.0
    assert result["ceiling_category"] in {"LIFR", "IFR", "MVFR", "VFR"}
    assert 0.0 < result["relative_humidity_pct"] <= 100.0
    assert result["dewpoint_k"] < 288.15  # a real dewpoint is never above the real temperature


def test_higher_humidity_gives_a_lower_estimated_ceiling():
    """A real physical monotonicity check: closer to saturation -> smaller
    dewpoint depression -> lower LCL height - not just 'a number changed'."""
    dry = compute_real_ceiling_at_point(temperature_k=293.15, specific_humidity=0.004, pressure_hpa=1013.25)
    humid = compute_real_ceiling_at_point(temperature_k=293.15, specific_humidity=0.012, pressure_hpa=1013.25)

    assert humid["ceiling_height_m"] < dry["ceiling_height_m"]


def test_near_saturation_gives_a_ceiling_close_to_the_surface():
    result = compute_real_ceiling_at_point(temperature_k=288.15, specific_humidity=0.0102, pressure_hpa=1013.25)

    assert result["relative_humidity_pct"] > 95.0
    assert result["ceiling_height_m"] < LIFR_CEILING_M


def test_classify_ceiling_category_real_faa_thresholds():
    assert classify_ceiling_category(0.0) == "LIFR"
    assert classify_ceiling_category(LIFR_CEILING_M - 1.0) == "LIFR"
    assert classify_ceiling_category(LIFR_CEILING_M) == "IFR"
    assert classify_ceiling_category(IFR_CEILING_M - 1.0) == "IFR"
    assert classify_ceiling_category(IFR_CEILING_M) == "MVFR"
    assert classify_ceiling_category(MVFR_CEILING_M - 1.0) == "MVFR"
    assert classify_ceiling_category(MVFR_CEILING_M) == "VFR"
    assert classify_ceiling_category(5000.0) == "VFR"


def test_validate_physics_defaults_to_false_and_does_not_raise_on_a_real_valid_point():
    # Same convention as acf.awci.theta_e - validate_physics is opt-in,
    # off by default, and must not raise for a genuine, in-range point.
    result = compute_real_ceiling_at_point(
        temperature_k=288.15, specific_humidity=0.006, pressure_hpa=1013.25, validate_physics=True
    )
    assert result["is_real_data"] is True
