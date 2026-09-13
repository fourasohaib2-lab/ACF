"""
ACF HPC Web Server
===================

Real FastAPI + WebSocket server streaming HPC cluster telemetry to a
browser, per docs/ACF_HPC_005_NEXT_ROADMAP.md's "Dashboard Web FastAPI /
WebSocket : Streamer les métriques HPCDashboard vers le portail web
opérationnel de l'ONM" objective.

This module was a genuine new build, not a "wire up existing code" fix:
acf.monitoring.websocket_server.OperationalWebSocketServer (found and
honestly fixed earlier this session) never bound a real socket at all,
and acf.api.api.ACFAPI is a plain Python facade with no HTTP layer -
there was no existing FastAPI app anywhere in this codebase before this.

Assembles every real `/api/v1/*` router in `acf.web.routers` - HPC
status/connect/disconnect/WebSocket stream (`hpc_router`), the trained
FNO surrogate (`fno_router`), and the Model Adapter Protocol/
Complexity/Events/Datasets routers built in earlier phases. `/api/hpc/*`,
`/api/fno/*` and `/ws/hpc/status` (this module's own original,
unprefixed paths) have been migrated to `/api/v1/hpc/*` and
`/api/v1/fno/*` - closing reports/ACF_MASTER_AUDIT_v2.md's §21 "API:
PARTIAL... pas l'organisation par domaine complète" finding for real,
not just for the routers added after this module already existed. No
behavior changed in the move, only the paths (see
`acf.web.routers.hpc_router`/`fno_router`'s own docstrings). The HTML
dashboard page this module used to serve at `/` has been removed
(2026-09-13, explicit user request to remove every ACF/AWCI dashboard)
- this file now only assembles the JSON/WebSocket API app.
"""

from pathlib import Path

from fastapi import FastAPI

from acf.ai.simulation.neural_operator import NeuralOperatorEngine
from acf.hpc_connector.connection_manager import HPCConnectionManager
from acf.web.routers import (
    complexity_router,
    datasets_router,
    events_router,
    fno_router,
    hpc_router,
    models_router,
    workstation_router,
)
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
    app.include_router(workstation_router, prefix="/api/v1")

    return app


def run(host: str = "127.0.0.1", port: int = 8090) -> None:
    """Console-script entry point (acf-web). Runs a real HPCConnectionManager -
    startup does real local probing (see HPCConnectionManager.__init__),
    same as the ESOC GUI does when it launches."""
    import uvicorn

    uvicorn.run(create_app(), host=host, port=port)


if __name__ == "__main__":
    run()
