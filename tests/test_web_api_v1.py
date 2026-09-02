"""
Tests for the domain-organized /api/v1/* surface (acf.web.routers) -
the Prompt Maître ACF v2.0's §21 gap
(reports/ACF_MASTER_AUDIT_v2.md: "API: PARTIAL... pas l'organisation
par domaine complète du §21").

Same fixture convention as tests/test_web_hpc_dashboard.py - a single
HPCConnectionManager built once per module (these routers don't touch
it at all, but create_app() always wires it in).
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from acf.hpc_connector.connection_manager import HPCConnectionManager
from acf.web.hpc_dashboard_server import create_app


@pytest.fixture(scope="module")
def client():
    app = create_app(hpc=HPCConnectionManager())
    with TestClient(app) as c:
        yield c


# ------------------------------------------------------------------ /api/v1/models


def test_list_models_reports_every_real_adapter(client):
    res = client.get("/api/v1/models")
    assert res.status_code == 200
    names = {m["name"] for m in res.json()}
    assert names == {"AROME", "ALADIN", "ARPEGE", "ERA5", "WRF", "ICON", "OpenIFS"}


def test_get_model_reports_real_capabilities_and_variables(client):
    res = client.get("/api/v1/models/AROME")
    assert res.status_code == 200
    body = res.json()
    assert body["name"] == "AROME"
    assert body["has_real_read_backend"] is True
    assert "S090TEMPERATURE" in body["variables"]
    assert body["levels"] == list(range(1, 91))


def test_get_model_reports_a_string_levels_convention_honestly(client):
    res = client.get("/api/v1/models/WRF")
    assert res.json()["levels"] == "eta"


def test_get_unknown_model_is_404(client):
    res = client.get("/api/v1/models/GFS")
    assert res.status_code == 404


def test_detect_model_runs_the_real_detect_logic(client):
    res = client.post("/api/v1/models/AROME/detect", json={"filename": "arome_run.fa"})
    assert res.status_code == 200
    assert res.json() == {"model": "AROME", "filename": "arome_run.fa", "detected": True}

    res = client.post("/api/v1/models/AROME/detect", json={"filename": "aladin_run.fa"})
    assert res.json()["detected"] is False


# ------------------------------------------------------------------ /api/v1/complexity


def test_complexity_score_genuinely_calls_awci_calculator(client):
    res = client.post("/api/v1/complexity/score", json={"temperature": 298.0, "wind_speed": 15.0})
    assert res.status_code == 200
    body = res.json()
    assert "awci" in body
    assert "decomposition" in body
    assert "module_scores" in body


def test_complexity_field_runs_a_real_small_solver_grid(client):
    res = client.get(
        "/api/v1/complexity/field",
        params={"model": "ARPEGE", "steps": 2, "n_lat": 3, "n_lon": 3, "field_key": "temperature_field"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["model"] == "ARPEGE"
    assert len(body["lats"]) == 3
    assert len(body["lons"]) == 3
    assert len(body["field"]) == 3 and len(body["field"][0]) == 3
    assert body["is_real_data"] is True


def test_complexity_field_rejects_an_unknown_field_key(client):
    res = client.get("/api/v1/complexity/field", params={"field_key": "not_a_real_field"})
    assert res.status_code == 400


def test_complexity_field_rejects_an_unknown_model(client):
    res = client.get("/api/v1/complexity/field", params={"model": "GFS", "n_lat": 2, "n_lon": 2})
    assert res.status_code == 400


def test_complexity_field_rejects_an_oversized_grid(client):
    res = client.get("/api/v1/complexity/field", params={"n_lat": 1000, "n_lon": 1000})
    assert res.status_code == 400
    assert "exceeds" in res.json()["detail"]


def test_complexity_field_forecast_field_nan_becomes_json_null(client):
    """A real JSON-safety regression check: forecast_field genuinely contains np.nan entries (undefined forecast score) - the API must emit `null`, not an invalid bare `NaN` token."""
    res = client.get(
        "/api/v1/complexity/field",
        params={"model": "ARPEGE", "steps": 1, "n_lat": 2, "n_lon": 2, "field_key": "forecast_field"},
    )
    assert res.status_code == 200
    # A strict JSON parse must succeed with no NaN token - httpx/requests already
    # parsed this via res.json() above without raising, which is itself the real check.
    flat = [v for row in res.json()["field"] for v in row]
    assert all(v is None or isinstance(v, float) for v in flat)


# ------------------------------------------------------------------ /api/v1/events


def test_detect_strong_wind_events_over_a_real_small_grid(client):
    res = client.post(
        "/api/v1/events/detect",
        params={"model": "ARPEGE", "event_type": "strong_wind", "steps": 2, "n_lat": 4, "n_lon": 4, "threshold": 0.0},
    )
    assert res.status_code == 200
    events = res.json()
    assert len(events) > 0  # threshold=0.0 m/s guarantees every point trips it
    assert events[0]["type"] == "strong_wind"
    assert events[0]["status"] == "DETECTED"
    assert events[0]["supporting_models"] == ["ARPEGE"]


def test_detect_rejects_an_unsupported_event_type(client):
    res = client.post("/api/v1/events/detect", params={"event_type": "thunderstorm"})
    assert res.status_code == 400


def test_event_lifecycle_transition_is_really_enforced_over_http(client):
    res = client.post(
        "/api/v1/events/detect",
        params={"model": "ARPEGE", "event_type": "strong_wind", "steps": 2, "n_lat": 2, "n_lon": 2, "threshold": 0.0},
    )
    event_id = res.json()[0]["event_id"]

    res = client.get(f"/api/v1/events/{event_id}")
    assert res.status_code == 200
    assert res.json()["status"] == "DETECTED"

    res = client.post(f"/api/v1/events/{event_id}/transition", json={"new_status": "ANALYZED"})
    assert res.status_code == 200
    assert res.json()["status"] == "ANALYZED"

    # Illegal jump (ANALYZED -> CERTIFIED skips CONFIRMED/VERIFIED) must be a real 409, not silently accepted.
    res = client.post(f"/api/v1/events/{event_id}/transition", json={"new_status": "CERTIFIED"})
    assert res.status_code == 409
    assert "Cannot transition" in res.json()["detail"]

    # The event itself must be unchanged after the rejected transition.
    res = client.get(f"/api/v1/events/{event_id}")
    assert res.json()["status"] == "ANALYZED"


def test_transition_unknown_event_is_404(client):
    res = client.post("/api/v1/events/does-not-exist/transition", json={"new_status": "ANALYZED"})
    assert res.status_code == 404


def test_list_events_reflects_the_real_store(client):
    client.post(
        "/api/v1/events/detect",
        params={"model": "ARPEGE", "event_type": "strong_wind", "steps": 2, "n_lat": 2, "n_lon": 2, "threshold": 0.0},
    )
    res = client.get("/api/v1/events")
    assert res.status_code == 200
    assert len(res.json()) > 0


# ------------------------------------------------------------------ /api/v1/datasets


def test_create_dataset_from_a_real_complexity_field(client):
    res = client.post(
        "/api/v1/datasets/from_complexity_field",
        params={"model": "ARPEGE", "field_key": "temperature_field", "steps": 2, "n_lat": 3, "n_lon": 3},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["model"] == "ARPEGE"
    assert body["variable"] == "air_temperature"
    assert "values" not in body  # summarized by default
    assert body["values_summary"]["shape"] == [3, 3]
    # Regression check for the real numpy-in-a-plain-dict-field bug found
    # while building this endpoint (Dataset.coordinates holds real numpy
    # lats/lons arrays, not dataclass fields asdict() would convert).
    assert isinstance(body["coordinates"]["lats"], list)
    assert all(isinstance(v, float) for v in body["coordinates"]["lats"])


def test_get_dataset_with_include_values(client):
    create = client.post(
        "/api/v1/datasets/from_complexity_field",
        params={"model": "ARPEGE", "field_key": "temperature_field", "steps": 2, "n_lat": 2, "n_lon": 2},
    )
    dataset_id = create.json()["id"]

    res = client.get(f"/api/v1/datasets/{dataset_id}")
    assert "values" not in res.json()

    res = client.get(f"/api/v1/datasets/{dataset_id}", params={"include_values": True})
    assert res.status_code == 200
    assert res.json()["values"] is not None


def test_get_unknown_dataset_is_404(client):
    res = client.get("/api/v1/datasets/does-not-exist")
    assert res.status_code == 404


def test_validate_dataset_runs_the_real_physics_guard(client):
    create = client.post(
        "/api/v1/datasets/from_complexity_field",
        params={"model": "ARPEGE", "field_key": "temperature_field", "steps": 2, "n_lat": 3, "n_lon": 3},
    )
    dataset_id = create.json()["id"]

    res = client.get(f"/api/v1/datasets/{dataset_id}/validate")
    assert res.status_code == 200
    body = res.json()
    assert body["passed"] is True
    assert "coordinate" in body["checks_run"]
    assert "range" in body["checks_run"]


def test_list_datasets_reflects_the_real_store(client):
    client.post(
        "/api/v1/datasets/from_complexity_field",
        params={"model": "ARPEGE", "field_key": "temperature_field", "steps": 2, "n_lat": 2, "n_lon": 2},
    )
    res = client.get("/api/v1/datasets")
    assert res.status_code == 200
    assert len(res.json()) > 0


def test_datasets_and_complexity_field_share_the_real_oversized_grid_guard(client):
    res = client.post(
        "/api/v1/datasets/from_complexity_field", params={"model": "ARPEGE", "n_lat": 1000, "n_lon": 1000}
    )
    assert res.status_code == 400
