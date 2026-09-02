"""
Tests for acf.web.hpc_dashboard_server - the real FastAPI/WebSocket HPC
dashboard server (docs/ACF_HPC_005_NEXT_ROADMAP.md's "Dashboard Web
FastAPI / WebSocket" objective).

A single HPCConnectionManager is constructed once for the whole module
(it does real local probing at construction time - slow to repeat per
test) and injected into create_app(), rather than letting the app build
its own lazily.
"""

import pytest
from fastapi.testclient import TestClient

from acf.ai.simulation.neural_operator import NeuralOperatorEngine
from acf.hpc_connector.connection_manager import HPCConnectionManager
from acf.web.hpc_dashboard_server import DEFAULT_FNO_CHECKPOINT, create_app


@pytest.fixture(scope="module")
def hpc():
    return HPCConnectionManager()


@pytest.fixture(scope="module")
def client(hpc):
    app = create_app(hpc=hpc)
    with TestClient(app) as c:
        yield c


def test_index_page_serves_html(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "ACF HPC Web Dashboard" in res.text
    assert "/ws/hpc/status" in res.text


def test_status_endpoint_reflects_real_manager_state(client, hpc):
    res = client.get("/api/hpc/status")
    assert res.status_code == 200
    data = res.json()

    # Every field must trace back to the real HPCConnectionManager - not
    # be fabricated by the web layer.
    assert data["connected"] == hpc.is_connected
    assert data["scheduler"] == hpc.scheduler.scheduler_name
    assert "telemetry" in data
    assert "gpu_info" in data
    assert "heartbeat" in data
    assert data["heartbeat"]["status"] in ("HEALTHY", "DISCONNECTED")


def test_status_never_claims_real_transport_without_one(client, hpc):
    """CORRECTED (caught before it shipped, same discipline as this
    session's ESOC toolbar fix): a naive implementation could read
    `connected` (HPCConnectionManager.connect()'s own workflow-completed
    flag, true even in offline/local dev mode - see its own NOTE) and
    have the web page claim a live cluster connection that was never
    really established. real_ssh_transport must reflect the honest
    ssh_connector.is_real_connection flag instead."""
    res = client.get("/api/hpc/status")
    data = res.json()
    assert data["real_ssh_transport"] == bool(getattr(hpc.ssh_connector, "is_real_connection", False))


def test_connect_endpoint_returns_real_outcome(client, hpc):
    res = client.post("/api/hpc/connect", params={"profile": "fennec"})
    assert res.status_code == 200
    data = res.json()
    # In this offline sandbox, the workflow completes (dev-mode design,
    # see HPCConnectionManager.connect()'s own NOTE) but no real
    # transport is ever established.
    assert data["connected"] is True
    assert data["real_ssh_transport"] is False


def test_disconnect_endpoint(client, hpc):
    client.post("/api/hpc/connect", params={"profile": "fennec"})
    res = client.post("/api/hpc/disconnect")
    assert res.status_code == 200
    data = res.json()
    assert data["connected"] is False


def test_websocket_streams_real_status(client):
    with client.websocket_connect("/ws/hpc/status") as ws:
        payload = ws.receive_json()
        assert "connected" in payload
        assert "telemetry" in payload
        # A second push confirms this is a genuine loop, not a one-shot reply.
        payload2 = ws.receive_json()
        assert "connected" in payload2


def test_create_app_without_injected_hpc_lazily_builds_one():
    """create_app(hpc=None) (the real application path, acf-web's own
    entry point) must not construct HPCConnectionManager at app-creation
    time - only on first actual request - so importing/creating the app
    stays fast and side-effect-free until it's really used."""
    app = create_app()
    assert app.state.hpc is None


def test_reference_fno_checkpoint_exists_and_is_used_by_default():
    """The reference checkpoint trained by scripts/train_fno_surrogate.py
    (this session's FNO axis) is committed at this exact path - the demo
    endpoint below depends on it actually being found by default."""
    assert DEFAULT_FNO_CHECKPOINT.exists()


def test_fno_predict_demo_uses_the_real_trained_surrogate(client):
    res = client.post("/api/fno/predict_demo", params={"n_lat": 16, "n_lon": 32})
    assert res.status_code == 200
    data = res.json()

    assert data["status"] == "PREDICTED_BY_TRAINED_SURROGATE"
    assert data["surrogate_final_train_loss"] is not None
    assert "predicted_field_mean_k" in data
    # Real physical temperature range, not a placeholder.
    assert 150.0 < data["predicted_field_mean_k"] < 400.0


def test_fno_predict_demo_honest_without_a_checkpoint():
    """CORRECTED (caught before it shipped): if no trained checkpoint is
    configured, this endpoint must say so plainly - not silently fall
    back to some other value."""
    app = create_app(hpc=HPCConnectionManager(), fno_checkpoint_path=None)
    with TestClient(app) as c:
        res = c.post("/api/fno/predict_demo")
    data = res.json()
    assert data["status"] == "NOT_PREDICTED_NO_TRAINED_SURROGATE_LOADED"
    assert "predicted_field_mean_k" not in data


def test_create_app_accepts_an_injected_neural_engine():
    engine = NeuralOperatorEngine()  # no checkpoint loaded
    app = create_app(hpc=HPCConnectionManager(), neural_engine=engine)
    assert app.state.neural_engine is engine
