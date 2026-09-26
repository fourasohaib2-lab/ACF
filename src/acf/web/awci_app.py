"""
Light FastAPI app serving only /api/v1/awci (no HPC/torch imports).

    acf-awci-web            # uvicorn on 127.0.0.1:8091
    acf-awci-web --auto     # the same, plus automatic download and deletion after a week (acf-awci-auto)
Data directory: ACF_AWCI_DATA_DIR (default <repo>/data/awci); domains: ACF_AWCI_DOMAINS_FILE.
Front: the built web/awci (ACF_AWCI_WEB_DIST, default <repo>/web/awci/dist) is served on "/" when present,
after the API routes, so the browser and the API share one origin (no CORS needed).
CORS: ACF_AWCI_CORS_ORIGINS (comma-separated), default none (same origin).
"""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from acf.awci.ops.domains import DEFAULT_DOMAINS_PATH, load_domains
from acf.awci.ops.store import CubeStore, data_root
from acf.web.awci_router import default_cloud_profile, default_profile, router
from acf.web.awci_wms import UrllibWmsFetcher, WmsRelay

DEFAULT_WEB_DIST = Path(__file__).resolve().parents[3] / "web" / "awci" / "dist"


def attach_awci_state(app: FastAPI, data_dir: Path | None = None, domains_file: Path | None = None) -> None:
    app.state.awci_store = CubeStore(data_dir)
    env_domains = os.environ.get("ACF_AWCI_DOMAINS_FILE")
    app.state.awci_domains = load_domains(domains_file or (Path(env_domains) if env_domains else DEFAULT_DOMAINS_PATH))
    app.state.awci_profile = default_profile()
    app.state.awci_cloud_profile = default_cloud_profile()
    cache = os.environ.get("ACF_AWCI_WMS_CACHE")
    app.state.awci_wms = WmsRelay(UrllibWmsFetcher(), Path(cache) if cache else (data_dir or data_root()) / ".wms-cache")


def create_awci_app(
    data_dir: Path | None = None, domains_file: Path | None = None, cors_origins: list[str] | None = None,
    web_dist: Path | None = None,
) -> FastAPI:
    app = FastAPI(title="AWCI Web API", version="1.0.0")
    attach_awci_state(app, data_dir, domains_file)
    origins = cors_origins if cors_origins is not None else [
        o for o in os.environ.get("ACF_AWCI_CORS_ORIGINS", "").split(",") if o
    ]
    if origins:
        app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["GET"], allow_headers=["*"],
                           expose_headers=["X-AWCI-Shape", "X-AWCI-Lats", "X-AWCI-Lons", "X-AWCI-Nodata",
                                           "X-AWCI-Unit", "X-AWCI-Attribution", "X-AWCI-Levels",
                                           "X-AWCI-Parts", "X-AWCI-Observed-At"])
    app.include_router(router, prefix="/api/v1")
    env_dist = os.environ.get("ACF_AWCI_WEB_DIST")
    dist = web_dist or (Path(env_dist) if env_dist else DEFAULT_WEB_DIST)
    if (dist / "index.html").exists():
        app.mount("/", StaticFiles(directory=dist, html=True), name="awci-web")
    return app


def run(host: str = "127.0.0.1", port: int = 8091) -> None:
    import uvicorn

    uvicorn.run(create_awci_app(), host=host, port=port)


def _die_with_parent() -> None:
    """In the child, before exec: ask Linux to send SIGTERM when the parent dies (prctl PR_SET_PDEATHSIG)."""
    import ctypes
    import signal

    pr_set_pdeathsig = 1
    ctypes.CDLL("libc.so.6", use_errno=True).prctl(pr_set_pdeathsig, signal.SIGTERM)


def main(argv: list[str] | None = None) -> int:
    """acf-awci-web [--host H] [--port P] [--auto [acf-awci-auto options]]

    With --auto, acf-awci-auto (automatic download and deletion after a week) runs beside the server as a
    child process on the same data directory, and stops with it; its own options follow (e.g. --ens)."""
    import argparse
    import subprocess
    import sys

    parser = argparse.ArgumentParser(prog="acf-awci-web", description="AWCI Web: API and dashboard")
    parser.add_argument("--host", default="127.0.0.1", help="127.0.0.1 (default) keeps the server local")
    parser.add_argument("--port", type=int, default=8091)
    parser.add_argument("--auto", action="store_true", help="download the data automatically (acf-awci-auto)")
    args, auto_args = parser.parse_known_args(argv)
    if auto_args and not args.auto:
        parser.error(f"unrecognized arguments: {' '.join(auto_args)}")
    if "--data-dir" in auto_args:  # the server and the downloader must share one directory
        parser.error("set the data directory with ACF_AWCI_DATA_DIR, not --data-dir, when using --auto")
    child = None
    if args.auto:
        # the downloader must not outlive the server: uvicorn re-raises SIGINT/SIGTERM after shutdown, so the
        # `finally` below is not reached on a signal; the kernel (Linux) and the child's own watch cover that
        child = subprocess.Popen([sys.executable, "-m", "acf.awci.ops.auto", "--parent-pid", str(os.getpid()), *auto_args],
                                 preexec_fn=_die_with_parent if sys.platform.startswith("linux") else None)
    try:
        run(args.host, args.port)
    finally:
        if child is not None:
            child.terminate()
            try:
                child.wait(timeout=30)
            except subprocess.TimeoutExpired:
                child.kill()
    return 0
