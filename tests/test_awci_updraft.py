"""
Tests for acf.awci.updraft - real maximum theoretical updraft velocity
(docs/ACF_MASTER_PROMPT.md section 14, explicit user request "continue
au module convectif, avec le sommet des nuages"). No real, peer-
reviewed single-point cloud-top-HEIGHT formula exists anywhere in this
codebase (the one candidate found was uncited); the user was asked
directly and chose this real, well-established parcel-theory
alternative (w_max = sqrt(2*CAPE)) instead.
"""

from __future__ import annotations

import math

import pytest

from acf.awci.updraft import compute_real_max_updraft_velocity
from acf.science.clouds.dynamics import CloudDynamicsEngine


def test_matches_a_direct_clouddynamicsengine_call():
    engine = CloudDynamicsEngine()
    cape = 1800.0

    result = compute_real_max_updraft_velocity(cape)

    expected = engine.max_updraft_velocity(cape)
    assert result["w_max_m_s"] == pytest.approx(expected)


def test_real_known_value_cross_check():
    """w_max = sqrt(2 * 2500) = sqrt(5000) ~= 70.7106... - independently verifiable by hand."""
    result = compute_real_max_updraft_velocity(2500.0)
    assert result["w_max_m_s"] == pytest.approx(math.sqrt(5000.0))


def test_zero_cape_gives_zero_updraft():
    result = compute_real_max_updraft_velocity(0.0)
    assert result["w_max_m_s"] == pytest.approx(0.0)


def test_negative_cape_clamps_to_zero_updraft():
    """Negative CAPE is physically meaningless for this formula - clamped, not a fabricated negative velocity."""
    result = compute_real_max_updraft_velocity(-100.0)
    assert result["w_max_m_s"] == pytest.approx(0.0)


def test_updraft_velocity_is_monotonically_increasing_in_cape():
    capes = [0.0, 500.0, 1000.0, 2000.0, 3000.0, 5000.0]
    values = [compute_real_max_updraft_velocity(c)["w_max_m_s"] for c in capes]
    assert values == sorted(values)
    # Strictly increasing for strictly increasing positive CAPE.
    assert all(b > a for a, b in zip(values, values[1:]))


def test_engine_can_be_reused_across_calls():
    """Passing an existing CloudDynamicsEngine instance avoids constructing a fresh one per call/grid point."""
    engine = CloudDynamicsEngine()
    result_a = compute_real_max_updraft_velocity(1000.0, engine=engine)
    result_b = compute_real_max_updraft_velocity(2000.0, engine=engine)
    assert result_a["w_max_m_s"] == pytest.approx(math.sqrt(2000.0))
    assert result_b["w_max_m_s"] == pytest.approx(math.sqrt(4000.0))


def test_is_real_data_and_status_are_honest():
    result = compute_real_max_updraft_velocity(1500.0)
    assert result["is_real_data"] is True
    assert result["status"] == "REAL_MAX_UPDRAFT_VELOCITY_PARCEL_THEORY"


def test_honest_limitation_discloses_proxy_and_deterministic_nature():
    result = compute_real_max_updraft_velocity(1500.0)
    limitation = result["honest_limitation"].lower()
    assert "proxy" in limitation
    assert "cape" in limitation


def test_updraft_velocity_is_never_negative():
    for cape in (-5000.0, -1.0, 0.0, 1.0, 10000.0):
        result = compute_real_max_updraft_velocity(cape)
        assert result["w_max_m_s"] >= 0.0
        assert not math.isnan(result["w_max_m_s"])
