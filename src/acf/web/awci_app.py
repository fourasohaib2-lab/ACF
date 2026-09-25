"""
Light FastAPI app serving only /api/v1/awci (no HPC/torch imports).

    acf-awci-web            # uvicorn on 127.0.0.1:8091
Data directory: ACF_AWCI_DATA_DIR (default <repo>/data/awci).
CORS: ACF_AWCI_CORS_ORIGINS (comma-separated), default none (same origin).
"""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from acf.awci.ops.domains import DEFAULT_DOMAINS_PATH, load_domains
from acf.awci.ops.store import CubeStore
from acf.web.routers.awci_router import default_profile, router


def attach_awci_state(app: FastAPI, data_dir: Path | None = None, domains_file: Path | None = None) -> None:
    app.state.awci_store = CubeStore(data_dir)
    app.state.awci_domains = load_domains(domains_file or DEFAULT_DOMAINS_PATH)
    app.state.awci_profile = default_profile()


def create_awci_app(
    data_dir: Path | None = None, domains_file: Path | None = None, cors_origins: list[str] | None = None
) -> FastAPI:
    app = FastAPI(title="AWCI Web API", version="1.0.0")
    attach_awci_state(app, data_dir, domains_file)
    origins = cors_origins if cors_origins is not None else [
        o for o in os.environ.get("ACF_AWCI_CORS_ORIGINS", "").split(",") if o
    ]
    if origins:
        app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["GET"], allow_headers=["*"],
                           expose_headers=["X-AWCI-Shape", "X-AWCI-Lats", "X-AWCI-Lons", "X-AWCI-Nodata",
                                           "X-AWCI-Unit", "X-AWCI-Attribution"])
    app.include_router(router, prefix="/api/v1")
    return app


def run(host: str = "127.0.0.1", port: int = 8091) -> None:
    import uvicorn

    uvicorn.run(create_awci_app(), host=host, port=port)
