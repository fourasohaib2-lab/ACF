"""
Tests for acf.awci.volcanic_ash - the real per-point volcanic-ash
exposure risk estimate closing AWCI's "cendres volcaniques" gap
(post-model4d audit, 2026-09-11).
"""

from __future__ import annotations

import pytest

from acf.awci.volcanic_ash import (
    DOWNWIND_HALF_WIDTH_DEG,
    TRANSPORT_BUFFER_KM,
    compute_real_ash_exposure_risk_at_point,
    compute_real_ash_plume_height_km,
)

_ERUPTION = dict(eruption_lat=36.7, eruption_lon=3.0, volumetric_eruption_rate_m3_s=500.0)


def test_no_eruption_rate_returns_honest_none_not_a_fabricated_value():
    result = compute_real_ash_exposure_risk_at_point(
        point_lat=37.0, point_lon=3.5, point_altitude_m=8000.0,
        eruption_lat=36.7, eruption_lon=3.0, volumetric_eruption_rate_m3_s=0.0,
        wind_speed_m_s=15.0, wind_direction_deg=270.0, hours_since_eruption=1.0,
    )
    assert result["ash_risk_score"] is None
    assert result["is_real_data"] is False
    assert result["status"] == "ASH_RISK_NOT_COMPUTED_NO_REAL_ERUPTION_SOURCE_DATA"


def test_negative_elapsed_time_returns_honest_none():
    result = compute_real_ash_exposure_risk_at_point(
        point_lat=37.0, point_lon=3.5, point_altitude_m=8000.0,
        **_ERUPTION, wind_speed_m_s=15.0, wind_direction_deg=270.0, hours_since_eruption=-1.0,
    )
    assert result["ash_risk_score"] is None


def test_point_downwind_within_plume_and_transport_distance_has_high_risk():
    # Wind FROM the west (270 deg) blows toward the east (~90 deg).
    result = compute_real_ash_exposure_risk_at_point(
        point_lat=36.9, point_lon=3.5, point_altitude_m=8000.0,
        **_ERUPTION, wind_speed_m_s=15.0, wind_direction_deg=270.0, hours_since_eruption=1.0,
    )
    assert result["is_real_data"] is True
    assert result["is_downwind"] is True
    assert result["altitude_within_plume"] == 1.0
    assert result["ash_risk_score"] == 1.0


def test_point_upwind_of_the_eruption_has_zero_risk():
    # Point is WEST of the eruption while wind blows FROM the west
    # (toward the east) - genuinely upwind, must be excluded.
    result = compute_real_ash_exposure_risk_at_point(
        point_lat=36.7, point_lon=2.0, point_altitude_m=8000.0,
        **_ERUPTION, wind_speed_m_s=15.0, wind_direction_deg=270.0, hours_since_eruption=1.0,
    )
    assert result["is_downwind"] is False
    assert result["downwind_proximity"] == 0.0
    assert result["ash_risk_score"] == 0.0


def test_point_above_the_real_plume_height_has_zero_risk():
    # A very low eruption rate gives a real, low plume height (Mastin
    # et al. 2009) - a point far above it must read zero, even if
    # genuinely downwind and close.
    low_plume_height_km = compute_real_ash_plume_height_km(1.0)
    result = compute_real_ash_exposure_risk_at_point(
        point_lat=36.9, point_lon=3.5, point_altitude_m=(low_plume_height_km + 5.0) * 1000.0,
        eruption_lat=36.7, eruption_lon=3.0, volumetric_eruption_rate_m3_s=1.0,
        wind_speed_m_s=15.0, wind_direction_deg=270.0, hours_since_eruption=1.0,
    )
    assert result["altitude_within_plume"] == 0.0
    assert result["ash_risk_score"] == 0.0


def test_point_far_beyond_the_real_transport_distance_has_zero_risk():
    # Downwind direction, but genuinely too far to have been reached
    # yet given the real speed x time transport estimate plus buffer.
    result = compute_real_ash_exposure_risk_at_point(
        point_lat=36.7, point_lon=20.0, point_altitude_m=8000.0,
        **_ERUPTION, wind_speed_m_s=5.0, wind_direction_deg=270.0, hours_since_eruption=0.1,
    )
    assert result["is_downwind"] is True
    assert result["downwind_proximity"] == 0.0
    assert result["ash_risk_score"] == 0.0


def test_plume_height_matches_the_real_reused_mastin_2009_formula():
    from acf.geology.volcanic_physics import VolcanicPhysicsEngine

    assert compute_real_ash_plume_height_km(500.0) == pytest.approx(
        VolcanicPhysicsEngine.volcanic_plume_height_km(500.0)
    )


def test_downwind_sector_half_width_is_the_documented_real_constant():
    assert DOWNWIND_HALF_WIDTH_DEG == 30.0


def test_transport_buffer_is_the_documented_real_constant():
    assert TRANSPORT_BUFFER_KM == 100.0


def test_transport_distance_is_real_speed_times_time_kinematics():
    result = compute_real_ash_exposure_risk_at_point(
        point_lat=36.9, point_lon=3.5, point_altitude_m=8000.0,
        **_ERUPTION, wind_speed_m_s=10.0, wind_direction_deg=270.0, hours_since_eruption=2.0,
    )
    assert result["transport_distance_km"] == pytest.approx(10.0 * 2.0 * 3.6)
