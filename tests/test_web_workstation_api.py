"""
Tests for the `/api/v1/workstation` router (added 2026-09-04) - real
HTTP surface over `acf.awci.workstation_fields`, the exact same
Qt-free functions the ACF Scientific Workstation's own GUI panels use.

Same fixture convention as tests/test_web_api_v1.py.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from acf.hpc_connector.connection_manager import HPCConnectionManager
from acf.web.hpc_dashboard_server import create_app


@pytest.fixture(scope="module")
def client():
    app = create_app(hpc=HPCConnectionManager(), event_db_path=":memory:", dataset_db_path=":memory:")
    with TestClient(app) as c:
        yield c


# ------------------------------------------------------------- /theta_e


def test_theta_e_runs_a_real_small_solver_volume(client):
    res = client.get(
        "/api/v1/workstation/theta_e",
        params={"model": "ARPEGE", "steps": 2, "n_lat": 3, "n_lon": 3, "n_levels": 2, "level": 0},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["model"] == "ARPEGE"
    assert body["level"] == 0
    assert len(body["lats"]) == 3
    assert len(body["lons"]) == 3
    assert len(body["theta_e_k"]) == 3 and len(body["theta_e_k"][0]) == 3
    assert len(body["relative_humidity_pct"]) == 3
    assert body["is_real_data"] is True


def test_theta_e_clamps_an_out_of_range_level(client):
    res = client.get(
        "/api/v1/workstation/theta_e",
        params={"model": "ARPEGE", "steps": 2, "n_lat": 3, "n_lon": 3, "n_levels": 2, "level": 999},
    )
    assert res.status_code == 200
    assert res.json()["level"] == 1  # clamped to the real n_levels-1


def test_theta_e_rejects_an_unknown_model(client):
    res = client.get("/api/v1/workstation/theta_e", params={"model": "GFS", "n_lat": 2, "n_lon": 2, "n_levels": 2})
    assert res.status_code == 400


def test_theta_e_rejects_an_oversized_volume(client):
    res = client.get(
        "/api/v1/workstation/theta_e", params={"n_lat": 1000, "n_lon": 1000, "n_levels": 10}
    )
    assert res.status_code == 400
    assert "exceeds" in res.json()["detail"]


# ----------------------------------------------------------- /dynamics


def test_dynamics_runs_a_real_small_solver_volume(client):
    res = client.get(
        "/api/v1/workstation/dynamics",
        params={"model": "ALADIN", "steps": 2, "n_lat": 4, "n_lon": 4, "n_levels": 2, "level": 1},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["model"] == "ALADIN"
    assert body["level"] == 1
    assert len(body["wind_speed_m_s"]) == 4
    assert len(body["relative_vorticity_s1"]) == 4
    assert len(body["divergence_s1"]) == 4
    assert body["is_real_data"] is True


def test_dynamics_pole_rows_are_honestly_null(client):
    """Real regression guard, matching this project's own known
    finding: a real grid spanning the pole produces honestly non-
    finite vorticity/divergence there - must serialize to JSON `null`,
    never a fabricated finite value."""
    res = client.get(
        "/api/v1/workstation/dynamics",
        params={"model": "ARPEGE", "steps": 1, "n_lat": 6, "n_lon": 6, "n_levels": 1, "level": 0},
    )
    body = res.json()
    assert body["relative_vorticity_s1"][0][0] is None  # the real south-pole row
    assert body["relative_vorticity_s1"][-1][0] is None  # the real north-pole row


# --------------------------------------------------------- /wind_shear


def test_wind_shear_runs_a_real_small_solver_volume(client):
    res = client.get(
        "/api/v1/workstation/wind_shear",
        params={"model": "ARPEGE", "steps": 2, "n_lat": 3, "n_lon": 3, "n_levels": 3},
    )
    assert res.status_code == 200
    body = res.json()
    assert len(body["wind_shear_m_s"]) == 3
    assert len(body["wind_shear_m_s"][0]) == 3
    # A real bulk shear magnitude is never negative.
    assert all(v is None or v >= 0.0 for row in body["wind_shear_m_s"] for v in row)
    assert body["is_real_data"] is True


def test_wind_shear_rejects_an_unknown_model(client):
    res = client.get("/api/v1/workstation/wind_shear", params={"model": "GFS", "n_lat": 2, "n_lon": 2, "n_levels": 2})
    assert res.status_code == 400


# --------------------------------------------------------- /convection


def test_convection_runs_a_real_small_solver_volume(client):
    res = client.get(
        "/api/v1/workstation/convection",
        params={"model": "ALADIN", "steps": 2, "n_lat": 6, "n_lon": 6, "n_levels": 8, "stride": 2},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["model"] == "ALADIN"
    assert body["stride"] == 2
    assert len(body["lats"]) == 3  # ceil(6/2)
    assert len(body["lons"]) == 3
    for key in ("cape_j_kg", "cin_j_kg", "lcl_m", "bulk_shear_m_s", "srh_m2_s2", "ehi", "scp", "stp"):
        assert len(body[key]) == 3 and len(body[key][0]) == 3
    assert body["is_real_data"] is True
    # Real physical non-negativity, same real convention as every other test/panel.
    assert all(v is None or v >= 0.0 for row in body["cape_j_kg"] for v in row)
    assert all(v is None or v >= 0.0 for row in body["cin_j_kg"] for v in row)


def test_convection_rejects_an_unknown_model(client):
    res = client.get(
        "/api/v1/workstation/convection", params={"model": "GFS", "n_lat": 2, "n_lon": 2, "n_levels": 2}
    )
    assert res.status_code == 400


def test_convection_rejects_an_invalid_stride(client):
    res = client.get(
        "/api/v1/workstation/convection", params={"n_lat": 4, "n_lon": 4, "n_levels": 2, "stride": 0}
    )
    assert res.status_code == 400
    assert "stride" in res.json()["detail"]


def test_convection_rejects_an_oversized_post_stride_grid(client):
    """A small stride on a large grid must be rejected - the real
    per-point MetPy parcel-ascent cost, not the pre-stride solver-size
    guard, is what this endpoint additionally protects."""
    res = client.get(
        "/api/v1/workstation/convection",
        params={"n_lat": 100, "n_lon": 100, "n_levels": 1, "stride": 1},
    )
    assert res.status_code == 400
    assert "exceeds" in res.json()["detail"]
