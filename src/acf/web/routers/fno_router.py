"""
`/api/v1/fno` - real HTTP surface over the trained FNO surface-
temperature surrogate (`acf.ai.simulation.fno_model`/`fno_training`).

Migrated from its original unprefixed path (`/api/fno/predict_demo`)
as the last piece of reports/ACF_MASTER_AUDIT_v2.md's §21 domain-
organization finding - see `acf.web.routers.hpc_router`'s own
docstring for the same migration on the HPC side. Same real behavior
as before, no new computation - only the path (and this module's
location) changed.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from acf.ai.simulation.neural_operator import NeuralOperatorEngine

router = APIRouter(prefix="/fno", tags=["fno"])

#: Repository-relative path to the reference FNO checkpoint trained by
#: scripts/train_fno_surrogate.py.
DEFAULT_FNO_CHECKPOINT = Path(__file__).resolve().parents[4] / "models" / "fno_surface_temperature_reference.pt"


def _get_neural_engine(request: Request) -> NeuralOperatorEngine:
    engine = getattr(request.app.state, "neural_engine", None)
    if engine is None:
        path = getattr(request.app.state, "fno_checkpoint_path", DEFAULT_FNO_CHECKPOINT)
        checkpoint = str(path) if path is not None and Path(path).exists() else None
        engine = NeuralOperatorEngine(fno_checkpoint_path=checkpoint)
        request.app.state.neural_engine = engine
    return engine


@router.post("/predict_demo")
async def api_fno_predict_demo(request: Request, n_lat: int = 32, n_lon: int = 64) -> JSONResponse:
    """
    Run the real trained FNO surrogate on a demo near-surface
    temperature field (a smooth synthetic pattern - there is no live
    gridded observation feeding this web dashboard), and report real,
    honest before/after statistics. Genuinely calls
    NeuralOperatorEngine.predict_surface_temperature() - not a canned
    response.
    """
    engine = _get_neural_engine(request)

    lat = np.linspace(-90, 90, n_lat)
    lon = np.linspace(-180, 180, n_lon, endpoint=False)
    lat_mesh, lon_mesh = np.meshgrid(lat, lon, indexing="ij")
    # Smooth, deterministic demo field (not a real observation) - see
    # acf.gui.dashboard.awci_synthetic_field for the same convention.
    demo_field = (288.0 - 0.5 * np.abs(lat_mesh) + 3.0 * np.sin(np.radians(lon_mesh) * 2)).astype(np.float32)

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
