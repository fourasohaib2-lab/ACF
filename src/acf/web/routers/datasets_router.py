"""
`/api/v1/datasets` - real HTTP surface over the Data Contract
(`acf.core.contracts.dataset.Dataset`, its `validate()` -> real
`PhysicsGuard`).

Storage note: same as `acf.web.routers.events_router` - a real, plain
in-memory dict on `request.app.state.dataset_store`, not a database.
Same disclosed reasoning: no Dataset persistence layer exists anywhere
in ACF yet; this is enough to genuinely exercise construction +
validation over HTTP across requests, not a claim of durable storage.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any
from uuid import uuid4

import numpy as np
from fastapi import APIRouter, HTTPException, Request
from fastapi.encoders import jsonable_encoder

from acf.core.contracts.dataset import Dataset
from acf.web.routers._solver_guard import run_complexity_field

router = APIRouter(prefix="/datasets", tags=["datasets"])

#: Every 2D field key compute_real_complexity_field() can genuinely
#: return - same set /api/v1/complexity/field validates against.
_VALID_FIELD_KEYS = (
    "awci_field",
    "physical_field",
    "forecast_field",
    "temperature_field",
    "wind_speed_field",
    "specific_humidity_field",
    "pressure_field_hpa",
)


def _get_store(request: Request) -> dict[str, Dataset]:
    store = getattr(request.app.state, "dataset_store", None)
    if store is None:
        store = {}
        request.app.state.dataset_store = store
    return store


def _numpy_to_native(obj: Any) -> Any:
    """
    Recursively replace any real numpy array/scalar with a plain
    Python list/float - found necessary while building this endpoint
    (not assumed): `dataclasses.asdict()` does NOT convert values
    nested inside a plain `dict` field (e.g. `Dataset.coordinates`,
    which `Dataset.from_real_field()` genuinely populates with real
    numpy `lats`/`lons` arrays) since those aren't dataclass fields
    themselves - `jsonable_encoder` then raises on the raw ndarray
    (verified: `TypeError` from both its `dict(obj)` and `vars(obj)`
    fallback attempts). Applied before `jsonable_encoder`, not instead
    of it - this only handles numpy, `jsonable_encoder` still handles
    everything else (datetime, timedelta, ...).
    """
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, np.generic):
        return obj.item()
    if isinstance(obj, dict):
        return {k: _numpy_to_native(v) for k, v in obj.items()}
    if isinstance(obj, list | tuple):
        return [_numpy_to_native(v) for v in obj]
    return obj


def _serialize(dataset: Dataset, include_values: bool) -> dict[str, Any]:
    """
    Real Dataset -> JSON. `values` is summarized (shape/min/max/mean)
    by default - the full real array is only included when
    `include_values=True`, since a real solver grid can be large.
    """
    fields = asdict(dataset)  # recursively converts nested Provenance/QualityInfo/UncertaintyInfo dataclasses too
    values = fields.pop("values", None)
    fields = _numpy_to_native(fields)  # e.g. Dataset.coordinates's real lats/lons arrays - see _numpy_to_native()'s own note
    encoded = jsonable_encoder(fields)  # datetime/timedelta -> real ISO/seconds, safe on everything left as plain Python
    if values is not None:
        arr = np.asarray(values)
        encoded["values_summary"] = {
            "shape": list(arr.shape),
            "min": float(np.min(arr)),
            "max": float(np.max(arr)),
            "mean": float(np.mean(arr)),
        }
        if include_values:
            encoded["values"] = arr.tolist()
    return encoded


@router.post("/from_complexity_field")
async def from_complexity_field(
    request: Request,
    model: str = "ARPEGE",
    field_key: str = "temperature_field",
    variable: str = "air_temperature",
    unit: str = "K",
    steps: int = 4,
    n_lat: int = 8,
    n_lon: int = 8,
    seed: int = 0,
) -> dict[str, Any]:
    """
    Genuinely run `CoupledEarthSolver` (same request-size guard as
    `/api/v1/complexity/field`), then build a real `Dataset` from it
    via `Dataset.from_real_field()` - the real Data Contract, not a
    hand-rolled dict. Stored (`dataset.id` keyed) so it can be
    re-fetched or re-validated afterwards.
    """
    if field_key not in _VALID_FIELD_KEYS:
        raise HTTPException(400, f"Unknown field_key {field_key!r} - expected one of {_VALID_FIELD_KEYS}")
    result = run_complexity_field(model=model, steps=steps, n_lat=n_lat, n_lon=n_lon, seed=seed)

    dataset_id = f"{model}-{field_key}-{uuid4().hex[:8]}"
    dataset = Dataset.from_real_field(result, field_key=field_key, dataset_id=dataset_id, variable=variable, unit=unit)

    _get_store(request)[dataset.id] = dataset
    return _serialize(dataset, include_values=False)


@router.get("")
async def list_datasets(request: Request) -> list[dict[str, Any]]:
    return [_serialize(d, include_values=False) for d in _get_store(request).values()]


@router.get("/{dataset_id}")
async def get_dataset(dataset_id: str, request: Request, include_values: bool = False) -> dict[str, Any]:
    store = _get_store(request)
    if dataset_id not in store:
        raise HTTPException(404, f"No dataset {dataset_id!r} in this server's dataset store")
    return _serialize(store[dataset_id], include_values=include_values)


@router.get("/{dataset_id}/validate")
async def validate_dataset(dataset_id: str, request: Request) -> dict[str, Any]:
    """Re-run the real Dataset.validate() (-> PhysicsGuard) on the stored dataset - genuinely recomputed, not cached from construction time."""
    store = _get_store(request)
    if dataset_id not in store:
        raise HTTPException(404, f"No dataset {dataset_id!r} in this server's dataset store")
    return jsonable_encoder(store[dataset_id].validate())
