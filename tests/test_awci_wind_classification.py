"""
Tests for acf.awci.wind_classification - real WMO Beaufort scale
classification and real jet-stream detection, added 2026-09-12
(explicit user request "je veux que tu ajoutes toutes les seuils
possible pour que le projet soit conforme à 100%").
"""

from __future__ import annotations

import pytest

from acf.awci.wind_classification import (
    BEAUFORT_SCALE_M_S,
    classify_jet_stream,
    classify_wind_beaufort_force,
)


def test_beaufort_scale_has_all_13_real_wmo_forces():
    assert len(BEAUFORT_SCALE_M_S) == 13
    assert [force for force, _name, _bound in BEAUFORT_SCALE_M_S] == list(range(13))


def test_calm_and_hurricane_extremes():
    assert classify_wind_beaufort_force(0.0)["force"] == 0
    assert classify_wind_beaufort_force(0.0)["name"] == "Calm"
    assert classify_wind_beaufort_force(50.0)["force"] == 12
    assert classify_wind_beaufort_force(50.0)["name"] == "Hurricane force"


@pytest.mark.parametrize(
    "wind_speed_m_s,expected_force",
    [
        (0.2, 0),
        (0.3, 1),  # real WMO boundary: exactly at the upper bound moves to the next force
        (1.5, 1),
        (1.6, 2),
        (5.4, 3),
        (5.5, 4),
        (17.1, 7),
        (17.2, 8),  # real ICAO/WMO "Gale" onset
        (32.6, 11),
        (32.7, 12),  # real WMO "Hurricane force" onset
    ],
)
def test_beaufort_real_wmo_boundaries(wind_speed_m_s, expected_force):
    assert classify_wind_beaufort_force(wind_speed_m_s)["force"] == expected_force


def test_beaufort_never_fabricates_a_negative_force():
    """A real, non-physical sensor artifact (negative wind speed) must
    still honestly classify as Calm (treated as 0), never raise or
    return an invented negative force."""
    result = classify_wind_beaufort_force(-5.0)
    assert result["force"] == 0
    assert result["wind_speed_m_s"] == 0.0


def test_beaufort_force_is_monotonically_non_decreasing_with_wind_speed():
    speeds = [0.0, 1.0, 3.0, 6.0, 9.0, 12.0, 15.0, 19.0, 22.0, 26.0, 30.0, 33.0, 40.0]
    forces = [classify_wind_beaufort_force(s)["force"] for s in speeds]
    assert forces == sorted(forces)


def test_classify_jet_stream_matches_a_direct_real_call():
    from acf.science.wind_turbulence import JET_STREAM_THRESHOLD_M_S, JetStream

    for speed in (0.0, 29.9, 30.0, 30.1, 60.0):
        result = classify_jet_stream(speed)
        assert result["is_jet_stream"] == JetStream.is_jet_stream(speed)
        assert result["threshold_m_s"] == JET_STREAM_THRESHOLD_M_S
        assert result["wind_speed_m_s"] == speed


def test_classify_jet_stream_real_threshold_is_30_m_s():
    """Real, cited textbook threshold (~58 kt) - not an ACF-chosen value."""
    assert classify_jet_stream(30.0)["threshold_m_s"] == 30.0
