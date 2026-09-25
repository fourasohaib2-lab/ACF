"""
Light FastAPI app serving only /api/v1/awci (no HPC/torch imports).

    acf-awci-web            # uvicorn on 127.0.0.1:8091
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
