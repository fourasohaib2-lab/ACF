"""
ACF HPC Web Dashboard Server
=============================

Real FastAPI + WebSocket server streaming HPC cluster telemetry to a
browser, per docs/ACF_HPC_005_NEXT_ROADMAP.md's "Dashboard Web FastAPI /
WebSocket : Streamer les métriques HPCDashboard vers le portail web
opérationnel de l'ONM" objective.

This module was a genuine new build, not a "wire up existing code" fix:
acf.monitoring.websocket_server.OperationalWebSocketServer (found and
honestly fixed earlier this session) never bound a real socket at all,
and acf.api.api.ACFAPI is a plain Python facade with no HTTP layer -
there was no existing FastAPI app anywhere in this codebase before this.

Assembles and serves the dashboard HTML page (`/`) plus every real
`/api/v1/*` router in `acf.web.routers` - HPC status/connect/
disconnect/WebSocket stream (`hpc_router`), the trained FNO surrogate
(`fno_router`), and the Model Adapter Protocol/Complexity/Events/
Datasets routers built in earlier phases. `/api/hpc/*`, `/api/fno/*`
and `/ws/hpc/status` (this module's own original, unprefixed paths)
have been migrated to `/api/v1/hpc/*` and `/api/v1/fno/*` - closing
reports/ACF_MASTER_AUDIT_v2.md's §21 "API: PARTIAL... pas
l'organisation par domaine complète" finding for real, not just for
the routers added after this module already existed. No behavior
changed in the move, only the paths (see `acf.web.routers.hpc_router`/
`fno_router`'s own docstrings) - this file itself now only assembles
the app and owns the dashboard's HTML/JS.
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from acf.ai.simulation.neural_operator import NeuralOperatorEngine
from acf.hpc_connector.connection_manager import HPCConnectionManager
from acf.web.routers import complexity_router, datasets_router, events_router, fno_router, hpc_router, models_router
from acf.web.routers.fno_router import DEFAULT_FNO_CHECKPOINT

__all__ = ["DEFAULT_FNO_CHECKPOINT", "create_app", "run"]


def create_app(
    hpc: HPCConnectionManager | None = None,
    neural_engine: NeuralOperatorEngine | None = None,
    fno_checkpoint_path: str | Path | None = DEFAULT_FNO_CHECKPOINT,
    event_db_path: str | Path | None = None,
    dataset_db_path: str | Path | None = None,
) -> FastAPI:
    """Build the FastAPI app.

    Parameters
    ----------
    hpc : HPCConnectionManager, optional
        Injected for tests (avoids repeated slow local probing across
        many test cases). Defaults to a real, lazily-constructed
        HPCConnectionManager for actual application use (see
        `acf.web.routers.hpc_router._get_hpc()`).
    neural_engine : NeuralOperatorEngine, optional
        Injected for tests. Defaults to a real, lazily-constructed one
        that loads fno_checkpoint_path if it exists (see
        `acf.web.routers.fno_router._get_neural_engine()`).
    fno_checkpoint_path : path to the trained FNO checkpoint, or None to
        disable the FNO endpoint's model loading (it will then always
        report NOT_PREDICTED_NO_TRAINED_SURROGATE_LOADED, honestly).
    event_db_path, dataset_db_path : real SQLite file path for
        `/api/v1/events`/`/api/v1/datasets`'s durable storage (see
        `acf.web.storage.SqliteDocumentStore`) - defaults to a real
        file under `<repo_root>/data/web/` for actual application use;
        tests should pass `":memory:"` (or a `tmp_path`) explicitly so
        repeated test runs don't accumulate real data or race each
        other over the same default file.
    """
    app = FastAPI(title="ACF HPC Web Dashboard")
    app.state.hpc = hpc  # may be None - constructed lazily on first use, see hpc_router._get_hpc()
    app.state.neural_engine = neural_engine
    app.state.fno_checkpoint_path = fno_checkpoint_path
    app.state.event_db_path = event_db_path  # None -> each router's own real default path
    app.state.dataset_db_path = dataset_db_path

    # Every real endpoint this app serves, domain-organized under
    # /api/v1/* (Prompt Maître ACF v2.0 §21) - see acf.web.routers's
    # own docstring for what each router wraps.
    app.include_router(models_router, prefix="/api/v1")
    app.include_router(complexity_router, prefix="/api/v1")
    app.include_router(events_router, prefix="/api/v1")
    app.include_router(datasets_router, prefix="/api/v1")
    app.include_router(hpc_router, prefix="/api/v1")
    app.include_router(fno_router, prefix="/api/v1")

    @app.get("/", response_class=HTMLResponse)
    async def index() -> str:
        return _INDEX_HTML

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

  <div id="raw">Connecting to /api/v1/hpc/ws ...</div>

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
  const res = await fetch('/api/v1/hpc/' + action, { method: 'POST' });
  const data = await res.json();
  render(data);
}

async function fnoPredict() {
  setText('fno-status', 'Running...', 'warn');
  const res = await fetch('/api/v1/fno/predict_demo', { method: 'POST' });
  const data = await res.json();
  const trained = data.status === 'PREDICTED_BY_TRAINED_SURROGATE';
  setText('fno-status', data.status, trained ? 'ok' : 'bad');
  setText('fno-input-mean', data.input_field_mean_k ? data.input_field_mean_k.toFixed(2) : '—');
  setText('fno-pred-mean', data.predicted_field_mean_k ? data.predicted_field_mean_k.toFixed(2) : '—');
  setText('fno-loss', data.surrogate_final_train_loss != null ? data.surrogate_final_train_loss.toFixed(5) : '—');
  document.getElementById('raw').textContent = JSON.stringify(data, null, 2);
}

const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
const ws = new WebSocket(proto + '//' + location.host + '/api/v1/hpc/ws');
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
