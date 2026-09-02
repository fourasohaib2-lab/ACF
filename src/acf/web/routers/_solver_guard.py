"""
Shared real-solver guard for the `/api/v1/complexity`, `/api/v1/events`
and `/api/v1/datasets` routers - all three genuinely run
`acf.awci.spatial_field.compute_real_complexity_field()` (a real
`CoupledEarthSolver` integration, not a lookup), so all three need the
same real protection against an HTTP caller requesting an unbounded
grid/step count. One shared function, not three copies of the same
check.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from fastapi import HTTPException

from acf.awci.spatial_field import compute_real_complexity_field
from acf.forecast.engine import MODEL_CONFIGS

#: A real solver run over HTTP must stay responsive - this is a
#: request-serving limit, not a scientific one (see
#: acf.awci.spatial_field's own module docstring for the real
#: CoupledEarthSolver these endpoints run).
MAX_FIELD_POINTS = 4096
MAX_STEPS = 50


def run_complexity_field(
    model: str,
    steps: int,
    n_lat: int,
    n_lon: int,
    level: int = 0,
    seed: int = 0,
) -> dict[str, Any]:
    """Validate real request-size limits, then genuinely run compute_real_complexity_field() - raises HTTPException(400) rather than letting an oversized request hang the server."""
    if model not in MODEL_CONFIGS:
        raise HTTPException(400, f"Unknown model {model!r} - expected one of {sorted(MODEL_CONFIGS)}")
    if n_lat < 1 or n_lon < 1:
        raise HTTPException(400, f"n_lat/n_lon must be >= 1, got n_lat={n_lat}, n_lon={n_lon}")
    if n_lat * n_lon > MAX_FIELD_POINTS:
        raise HTTPException(
            400,
            f"n_lat*n_lon={n_lat * n_lon} exceeds this API's real max of {MAX_FIELD_POINTS} grid points per "
            f"request (protects the server from an unbounded real CoupledEarthSolver run over HTTP)",
        )
    if steps < 1 or steps > MAX_STEPS:
        raise HTTPException(400, f"steps must be in [1, {MAX_STEPS}], got {steps}")
    return compute_real_complexity_field(model=model, steps=steps, n_lat=n_lat, n_lon=n_lon, level=level, seed=seed)


def field_to_json_safe_list(arr: np.ndarray) -> list[list[float | None]]:
    """
    A 2D real field as nested JSON-safe lists, NaN converted to `null`.

    `compute_real_complexity_field()`'s own `forecast_field` genuinely
    contains real `np.nan` entries where a forecast score was
    undefined (its own docstring's "None-not-0.0 discipline") -
    `numpy.ndarray.tolist()` alone turns those into Python `float`
    NaNs, which `json.dumps` emits as a bare `NaN` token that is valid
    Python but NOT valid JSON (a real trap for any strict JSON client,
    e.g. JavaScript's `JSON.parse`) - converted to `null` here instead,
    a real, standard, round-trippable JSON value for "undefined".
    """
    return [[None if isinstance(v, float) and np.isnan(v) else float(v) for v in row] for row in arr.tolist()]
