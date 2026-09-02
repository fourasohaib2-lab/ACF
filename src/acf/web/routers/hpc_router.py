"""
`/api/v1/hpc` - real HTTP + WebSocket surface over
`acf.hpc_connector.connection_manager.HPCConnectionManager`.

Migrated from its original unprefixed paths (`/api/hpc/status`,
`/api/hpc/connect`, `/api/hpc/disconnect`, `/ws/hpc/status`) as the
last piece of reports/ACF_MASTER_AUDIT_v2.md's §21 domain-organization
finding - `acf.web.hpc_dashboard_server`'s own docstring had
deliberately deferred this exact move ("real, separate work"). Same
real behavior as before, no new computation - only the paths, and this
module's location, changed. `acf.web.hpc_dashboard_server.create_app()`
still assembles the app and owns the dashboard's HTML/JS (now pointed
at these new paths).

Honesty note (same discipline as when this was first built): every
field in `/status` and every WebSocket push is `HPCConnectionManager`'s
own real, already-audited data, not reinvented or embellished here.
`connected` (the 11-step connection workflow completed, true even in
local/offline development mode - see `HPCConnectionManager.connect()`'s
own NOTE) is deliberately distinct from `real_ssh_transport`
(`ssh_connector.is_real_connection` - only true when a live Paramiko
transport was actually confirmed), so this page can never claim a live
cluster connection that was never really established.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from acf.hpc_connector.connection_manager import HPCConnectionManager

logger = logging.getLogger("acf.web")

router = APIRouter(prefix="/hpc", tags=["hpc"])

#: Seconds between WebSocket status pushes to each connected browser.
PUSH_INTERVAL_SECONDS = 2.0


def _get_hpc(conn: Request | WebSocket) -> HPCConnectionManager:
    """Real, lazily-constructed HPCConnectionManager on `conn.app.state.hpc` - shared by both HTTP request handlers and the WebSocket handler below (both are real Starlette `HTTPConnection` subclasses with an `.app`)."""
    hpc = getattr(conn.app.state, "hpc", None)
    if hpc is None:
        hpc = HPCConnectionManager()
        conn.app.state.hpc = hpc
    return hpc


def _hpc_status(hpc: HPCConnectionManager) -> dict[str, Any]:
    """Build the real, honest status payload from HPCConnectionManager - every value comes directly from its own already-audited methods."""
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


@router.get("/status")
async def api_status(request: Request) -> JSONResponse:
    return JSONResponse(_hpc_status(_get_hpc(request)))


@router.post("/connect")
async def api_connect(request: Request, profile: str = "fennec") -> JSONResponse:
    """Genuinely attempt HPCConnectionManager.connect() off the event loop (real, potentially slow, blocking I/O - see its own docstring), then return the real resulting status."""
    hpc = _get_hpc(request)
    loop = asyncio.get_running_loop()
    try:
        await loop.run_in_executor(None, hpc.connect, profile)
    except Exception as exc:  # noqa: BLE001 - report, don't crash the request
        logger.exception("HPC connect(%r) raised", profile)
        return JSONResponse({"error": str(exc)}, status_code=502)
    return JSONResponse(_hpc_status(hpc))


@router.post("/disconnect")
async def api_disconnect(request: Request) -> JSONResponse:
    hpc = _get_hpc(request)
    hpc.disconnect()
    return JSONResponse(_hpc_status(hpc))


@router.websocket("/ws")
async def ws_status(websocket: WebSocket) -> None:
    """Push real HPC status every PUSH_INTERVAL_SECONDS until the client disconnects. Each push is a fresh call into HPCConnectionManager - genuinely live, not a cached snapshot."""
    await websocket.accept()
    hpc = _get_hpc(websocket)
    try:
        while True:
            await websocket.send_json(_hpc_status(hpc))
            await asyncio.sleep(PUSH_INTERVAL_SECONDS)
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected from /api/v1/hpc/ws")
