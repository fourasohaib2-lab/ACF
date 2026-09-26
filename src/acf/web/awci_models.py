"""
Deterministic model of a request (SP6): every cube route accepts `model=ifs|gfs` (default ifs).

The IFS cubes stay at the data root (unchanged layout), other models in <root>/<model>
(acf.awci.ops.store.model_root); observations and the IFS ensemble live at the data root whatever the model.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import HTTPException, Request

from acf.awci.ops.store import MODELS, CubeStore


def request_model(request: Request) -> str:
    model = request.query_params.get("model", "ifs")
    if model not in MODELS:
        raise HTTPException(422, f"unknown model {model!r} (known: {', '.join(MODELS)})")
    return model


def model_store(request: Request) -> CubeStore:
    stores: dict[str, CubeStore] = request.app.state.awci_stores
    return stores[request_model(request)]


def data_root(request: Request) -> Path:
    """Root of the data directory (observations, ensemble), independent of the model."""
    return Path(request.app.state.awci_store.root)
