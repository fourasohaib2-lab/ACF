"""
Tests for acf.awci.microburst - connecting the already-real, already-
cited acf.aviation.hazards.aviation_hazards "microburst_windshear"
encyclopedia entry to a live diagnostic (post-model4d audit,
2026-09-11).
"""

from __future__ import annotations

import pytest

from acf.awci.microburst import (
    ALTITUDE_RELEVANCE_BUFFER_M,
    MICROBURST_ALERT_ALTITUDE_M,
    MICROBURST_ALERT_SHEAR_M_S,
    compute_real_microburst_risk_at_point,
    get_microburst_hazard_reference,
)


def test_thresholds_match_the_real_cited_icao_values():
    # 30 kt and 1500 ft, converted to SI - see module docstring.
    assert MICROBURST_ALERT_SHEAR_M_S == pytest.approx(30.0 * 0.514444)
    assert MICROBURST_ALERT_ALTITUDE_M == pytest.approx(1500.0 * 0.3048)


def test_get_microburst_hazard_reference_returns_the_real_registry_entry():
    ref = get_microburst_hazard_reference()

    assert ref is not None
    assert ref.key == "microburst_windshear"
    assert "ICAO Doc 9837" in ref.references
    assert "30" in ref.icao_thresholds["MICROBURST_ALERT"]


def test_strong_shear_high_cape_low_altitude_gives_high_risk():
    result = compute_real_microburst_risk_at_point(
        wind_shear_m_s=MICROBURST_ALERT_SHEAR_M_S, cape=5000.0, altitude_m=100.0
    )

    assert result["shear_alert_proximity"] == 1.0
    assert result["convective_source_proximity"] == 1.0
    assert result["low_altitude_relevance"] == 1.0
    assert result["microburst_risk_score"] == 1.0


def test_cruise_altitude_gives_zero_risk_regardless_of_shear_and_cape():
    result = compute_real_microburst_risk_at_point(
        wind_shear_m_s=MICROBURST_ALERT_SHEAR_M_S, cape=5000.0, altitude_m=10000.0
    )

    assert result["low_altitude_relevance"] == 0.0
    assert result["microburst_risk_score"] == 0.0


def test_zero_cape_gives_zero_risk_regardless_of_shear_and_altitude():
    result = compute_real_microburst_risk_at_point(
        wind_shear_m_s=MICROBURST_ALERT_SHEAR_M_S, cape=0.0, altitude_m=100.0
    )

    assert result["convective_source_proximity"] == 0.0
    assert result["microburst_risk_score"] == 0.0


def test_calm_shear_gives_zero_risk_regardless_of_cape_and_altitude():
    result = compute_real_microburst_risk_at_point(wind_shear_m_s=0.0, cape=5000.0, altitude_m=100.0)

    assert result["shear_alert_proximity"] == 0.0
    assert result["microburst_risk_score"] == 0.0


def test_risk_is_multiplicative_across_all_three_real_preconditions():
    result = compute_real_microburst_risk_at_point(
        wind_shear_m_s=MICROBURST_ALERT_SHEAR_M_S / 2.0, cape=2500.0, altitude_m=100.0
    )

    assert result["microburst_risk_score"] == pytest.approx(
        result["shear_alert_proximity"] * result["convective_source_proximity"] * result["low_altitude_relevance"]
    )


def test_altitude_relevance_ramps_down_over_the_documented_buffer():
    at_threshold = compute_real_microburst_risk_at_point(
        wind_shear_m_s=MICROBURST_ALERT_SHEAR_M_S, cape=5000.0, altitude_m=MICROBURST_ALERT_ALTITUDE_M
    )
    beyond_buffer = compute_real_microburst_risk_at_point(
        wind_shear_m_s=MICROBURST_ALERT_SHEAR_M_S,
        cape=5000.0,
        altitude_m=MICROBURST_ALERT_ALTITUDE_M + ALTITUDE_RELEVANCE_BUFFER_M,
    )

    assert at_threshold["low_altitude_relevance"] == 1.0
    assert beyond_buffer["low_altitude_relevance"] == 0.0


def test_negative_shear_is_treated_as_calm_not_negative_risk():
    result = compute_real_microburst_risk_at_point(wind_shear_m_s=-5.0, cape=5000.0, altitude_m=100.0)
    assert result["shear_alert_proximity"] == 0.0
