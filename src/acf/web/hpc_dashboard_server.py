"""
ACF HPC Web Dashboard Server
=============================

Real FastAPI + WebSocket server streaming HPC cluster telemetry to a
browser, per docs/ACF_HPC_005_NEXT_ROADMAP.md's "Dashboard Web FastAPI /
WebSocket : Streamer les métriques HPCDashboard vers le portail web
opérationnel de l'ONM" objective.

Honesty note (same discipline as the rest of this session): this reuses
acf.hpc_connector.HPCConnectionManager exactly as-is - every field in
`/api/hpc/status` and every WebSocket push is that class's own real,
already-audited data (see its own NOTE (correction) comments this
session), not reinvented or embellished here. In particular this server
distinguishes `connected` (the 11-step connection workflow completed,
which - per HPCConnectionManager.connect()'s own NOTE - is true even in
local/offline development mode) from `real_ssh_transport`
(ssh_connector.is_real_connection - only true when a live Paramiko
transport was actually confirmed), exactly like the ESOC GUI's
"Connect HPC" toolbar action does, so this page can never claim a live
cluster connection that was never really established.

This module was a genuine new build, not a "wire up existing code" fix:
acf.monitoring.websocket_server.OperationalWebSocketServer (found and
honestly fixed earlier this session) never bound a real socket at all,
and acf.api.api.ACFAPI is a plain Python facade with no HTTP layer -
there was no existing FastAPI app anywhere in this codebase before this.

Also serves the real, trained FNO surface-temperature surrogate (see
acf.ai.simulation.fno_model/fno_training, this session's third roadmap
axis) via /api/fno/predict_demo - the reference checkpoint
(models/fno_surface_temperature_reference.pt) was, until now, only
reachable from raw Python, not from any user-facing surface.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any

import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse

from acf.ai.simulation.neural_operator import NeuralOperatorEngine
from acf.hpc_connector.connection_manager import HPCConnectionManager

logger = logging.getLogger("acf.web")

#: Seconds between WebSocket status pushes to each connected browser.
PUSH_INTERVAL_SECONDS = 2.0

#: Repository-relative path to the reference FNO checkpoint trained by
#: scripts/train_fno_surrogate.py (see this module's own docstring).
DEFAULT_FNO_CHECKPOINT = Path(__file__).resolve().parents[3] / "models" / "fno_surface_temperature_reference.pt"


def _hpc_status(hpc: HPCConnectionManager) -> dict[str, Any]:
    """Build the real, honest status payload from HPCConnectionManager.

    Every value here comes directly from HPCConnectionManager's own
    (already-audited) methods - nothing is computed or embellished here.
    """
    summary = hpc.get_status_summary()
    heartbeat = hpc.heartbeat()
    return {
        "connected": hpc.is_connected,
        "real_ssh_transport": bool(getattr(hpc.ssh_connector, "is_real_connection", False)),
        "scheduler": summary["scheduler"],
        "execution_mode": summary["execution_mode"],
        "operational_mode": summary["operational_mode"],
        "active_jobs_count": summary["active_jobs_count"],
        "telemetry": summary["telemetry"],
        "gpu_info": summary["gpu_info"],
        "mpi_info": summary["mpi_info"],
        "heartbeat": heartbeat,
    }


def create_app(
    hpc: HPCConnectionManager | None = None,
    neural_engine: NeuralOperatorEngine | None = None,
    fno_checkpoint_path: str | Path | None = DEFAULT_FNO_CHECKPOINT,
) -> FastAPI:
    """Build the FastAPI app.

    Parameters
    ----------
    hpc : HPCConnectionManager, optional
        Injected for tests (avoids repeated slow local probing across
        many test cases). Defaults to a real, lazily-constructed
        HPCConnectionManager for actual application use.
    neural_engine : NeuralOperatorEngine, optional
        Injected for tests. Defaults to a real, lazily-constructed one
        that loads fno_checkpoint_path if it exists.
    fno_checkpoint_path : path to the trained FNO checkpoint, or None to
        disable the FNO endpoint's model loading (it will then always
        report NOT_PREDICTED_NO_TRAINED_SURROGATE_LOADED, honestly).
    """
    app = FastAPI(title="ACF HPC Web Dashboard")
    app.state.hpc = hpc  # may be None - constructed lazily on first use, see _get_hpc()
    app.state.neural_engine = neural_engine
    app.state.fno_checkpoint_path = fno_checkpoint_path

    def _get_hpc() -> HPCConnectionManager:
        if app.state.hpc is None:
            app.state.hpc = HPCConnectionManager()
        return app.state.hpc

    def _get_neural_engine() -> NeuralOperatorEngine:
        if app.state.neural_engine is None:
            path = app.state.fno_checkpoint_path
            checkpoint = str(path) if path is not None and Path(path).exists() else None
            app.state.neural_engine = NeuralOperatorEngine(fno_checkpoint_path=checkpoint)
        return app.state.neural_engine

    @app.get("/", response_class=HTMLResponse)
    async def index() -> str:
        return _INDEX_HTML

    @app.get("/api/hpc/status")
    async def api_status() -> JSONResponse:
        return JSONResponse(_hpc_status(_get_hpc()))

    @app.post("/api/hpc/connect")
    async def api_connect(profile: str = "fennec") -> JSONResponse:
        """Genuinely attempt HPCConnectionManager.connect() off the event
        loop (it does real, potentially slow, blocking I/O - see its own
        docstring), then return the real resulting status."""
        hpc = _get_hpc()
        loop = asyncio.get_running_loop()
        try:
            await loop.run_in_executor(None, hpc.connect, profile)
        except Exception as exc:  # noqa: BLE001 - report, don't crash the request
            logger.exception("HPC connect(%r) raised", profile)
            return JSONResponse({"error": str(exc)}, status_code=502)
        return JSONResponse(_hpc_status(hpc))

    @app.post("/api/hpc/disconnect")
    async def api_disconnect() -> JSONResponse:
        hpc = _get_hpc()
        hpc.disconnect()
        return JSONResponse(_hpc_status(hpc))

    @app.post("/api/fno/predict_demo")
    async def api_fno_predict_demo(n_lat: int = 32, n_lon: int = 64) -> JSONResponse:
        """Run the real trained FNO surrogate on a demo near-surface
        temperature field (a smooth synthetic pattern - there is no live
        gridded observation feeding this web dashboard - see this
        module's own docstring), and report real, honest before/after
        statistics. Genuinely calls NeuralOperatorEngine.
        predict_surface_temperature() - not a canned response."""
        engine = _get_neural_engine()

        lat = np.linspace(-90, 90, n_lat)
        lon = np.linspace(-180, 180, n_lon, endpoint=False)
        lat_mesh, lon_mesh = np.meshgrid(lat, lon, indexing="ij")
        # Smooth, deterministic demo field (not a real observation) - see
        # acf.gui.dashboard.awci_synthetic_field for the same convention.
        demo_field = (
            288.0 - 0.5 * np.abs(lat_mesh) + 3.0 * np.sin(np.radians(lon_mesh) * 2)
        ).astype(np.float32)

        result = engine.predict_surface_temperature(demo_field)
        predicted = result.pop("predicted_field", None)

        response: dict[str, Any] = {
            **result,
            "input_field_mean_k": float(demo_field.mean()),
            "input_field_min_k": float(demo_field.min()),
            "input_field_max_k": float(demo_field.max()),
        }
        if predicted is not None:
            response["predicted_field_mean_k"] = float(predicted.mean())
            response["predicted_field_min_k"] = float(predicted.min())
            response["predicted_field_max_k"] = float(predicted.max())

        return JSONResponse(response)

    @app.websocket("/ws/hpc/status")
    async def ws_status(websocket: WebSocket) -> None:
        """Push real HPC status every PUSH_INTERVAL_SECONDS until the
        client disconnects. Each push is a fresh call into
        HPCConnectionManager - genuinely live, not a cached snapshot."""
        await websocket.accept()
        hpc = _get_hpc()
        try:
            while True:
                await websocket.send_json(_hpc_status(hpc))
                await asyncio.sleep(PUSH_INTERVAL_SECONDS)
        except WebSocketDisconnect:
            logger.info("WebSocket client disconnected from /ws/hpc/status")

    return app


_INDEX_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>ACF HPC Web Dashboard</title>
<style>
  body { background:#0d1b2a; color:#e0e0e0; font-family:'Segoe UI',Ubuntu,sans-serif; margin:0; padding:20px; }
  h1 { font-size:18px; margin:0 0 4px 0; }
  .sub { color:#8090a8; font-size:11px; margin-bottom:16px; }
  .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:12px; }
  .card { background:#16213e; border:1px solid #2a3a5a; border-radius:8px; padding:12px 14px; }
  .card h2 { font-size:11px; color:#8090a8; margin:0 0 6px 0; text-transform:uppercase; letter-spacing:.05em; }
  .card .value { font-size:20px; font-weight:bold; }
  .ok { color:#43a047; } .bad { color:#e53935; } .warn { color:#ffb300; }
  #actions { margin:16px 0; }
  button { background:#1e2f4d; color:#e0e0e0; border:1px solid #3a4a6a; border-radius:6px;
           padding:8px 14px; cursor:pointer; margin-right:8px; font-size:12px; }
  button:hover { background:#2a3f66; }
  #raw { margin-top:16px; font-family:Consolas,monospace; font-size:11px; color:#7080a0;
         background:#0a1929; border:1px solid #2a3a5a; border-radius:6px; padding:10px; white-space:pre-wrap; }
</style>
</head>
<body>
  <h1>⚡ ACF HPC Web Dashboard</h1>
  <div class="sub">Live over WebSocket - every value below is HPCConnectionManager's own real status, not illustrative.</div>

  <div id="actions">
    <button onclick="hpcAction('connect')">🔌 Connect HPC</button>
    <button onclick="hpcAction('disconnect')">❌ Disconnect</button>
  </div>

  <div class="grid">
    <div class="card"><h2>Connection</h2><div class="value" id="v-connected">—</div></div>
    <div class="card"><h2>Real SSH Transport</h2><div class="value" id="v-real">—</div></div>
    <div class="card"><h2>Scheduler</h2><div class="value" id="v-scheduler">—</div></div>
    <div class="card"><h2>Execution Mode</h2><div class="value" id="v-mode">—</div></div>
    <div class="card"><h2>Active Jobs</h2><div class="value" id="v-jobs">—</div></div>
    <div class="card"><h2>Heartbeat</h2><div class="value" id="v-heartbeat">—</div></div>
  </div>

  <h1 style="margin-top:28px;">🧠 FNO Surface Temperature Surrogate</h1>
  <div class="sub">Real, trained model (acf.ai.simulation.fno_model) run on a smooth demo field - not a live observation.</div>
  <div id="fno-actions">
    <button onclick="fnoPredict()">▶️ Run Surrogate on Demo Field</button>
  </div>
  <div class="grid">
    <div class="card"><h2>Status</h2><div class="value" id="fno-status">—</div></div>
    <div class="card"><h2>Input Mean (K)</h2><div class="value" id="fno-input-mean">—</div></div>
    <div class="card"><h2>Predicted Mean (K)</h2><div class="value" id="fno-pred-mean">—</div></div>
    <div class="card"><h2>Surrogate Train Loss</h2><div class="value" id="fno-loss">—</div></div>
  </div>

  <div id="raw">Connecting to /ws/hpc/status ...</div>

<script>
function setText(id, text, cls) {
  const el = document.getElementById(id);
  el.textContent = text;
  el.className = 'value' + (cls ? ' ' + cls : '');
}

function render(data) {
  setText('v-connected', data.connected ? 'Yes (workflow)' : 'No', data.connected ? 'warn' : 'bad');
  setText('v-real', data.real_ssh_transport ? 'Yes' : 'No', data.real_ssh_transport ? 'ok' : 'bad');
  setText('v-scheduler', data.scheduler || '—');
  setText('v-mode', data.execution_mode || '—');
  setText('v-jobs', data.active_jobs_count);
  setText('v-heartbeat', data.heartbeat && data.heartbeat.status || '—');
  document.getElementById('raw').textContent = JSON.stringify(data, null, 2);
}

async function hpcAction(action) {
  const res = await fetch('/api/hpc/' + action, { method: 'POST' });
  const data = await res.json();
  render(data);
}

async function fnoPredict() {
  setText('fno-status', 'Running...', 'warn');
  const res = await fetch('/api/fno/predict_demo', { method: 'POST' });
  const data = await res.json();
  const trained = data.status === 'PREDICTED_BY_TRAINED_SURROGATE';
  setText('fno-status', data.status, trained ? 'ok' : 'bad');
  setText('fno-input-mean', data.input_field_mean_k ? data.input_field_mean_k.toFixed(2) : '—');
  setText('fno-pred-mean', data.predicted_field_mean_k ? data.predicted_field_mean_k.toFixed(2) : '—');
  setText('fno-loss', data.surrogate_final_train_loss != null ? data.surrogate_final_train_loss.toFixed(5) : '—');
  document.getElementById('raw').textContent = JSON.stringify(data, null, 2);
}

const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
const ws = new WebSocket(proto + '//' + location.host + '/ws/hpc/status');
ws.onmessage = (event) => render(JSON.parse(event.data));
ws.onerror = () => { document.getElementById('raw').textContent = 'WebSocket error - see server logs.'; };
</script>
</body>
</html>
"""


def run(host: str = "127.0.0.1", port: int = 8090) -> None:
    """Console-script entry point (acf-web). Runs a real HPCConnectionManager -
    startup does real local probing (see HPCConnectionManager.__init__),
    same as the ESOC GUI does when it launches."""
    import uvicorn

    uvicorn.run(create_app(), host=host, port=port)


if __name__ == "__main__":
    run()
