"""
Shared real-solver guard for the `/api/v1/complexity`, `/api/v1/events`,
`/api/v1/datasets` and (added 2026-09-04) `/api/v1/workstation` routers
- all genuinely run a real `CoupledEarthSolver` integration (not a
lookup), so all need the same real protection against an HTTP caller
requesting an unbounded grid/step count. One shared set of functions,
not N copies of the same check.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np
from fastapi import HTTPException

from acf.awci.spatial_field import compute_real_complexity_field
from acf.awci.vertical_field import compute_real_complexity_volume
from acf.forecast.engine import MODEL_CONFIGS

#: A real solver run over HTTP must stay responsive - this is a
#: request-serving limit, not a scientific one (see
#: acf.awci.spatial_field's own module docstring for the real
#: CoupledEarthSolver these endpoints run).
MAX_FIELD_POINTS = 4096
MAX_STEPS = 50
#: Same real reasoning as MAX_FIELD_POINTS above, extended to a full
#: (n_levels, n_lat, n_lon) volume request - a real 3D CoupledEarthSolver
#: run is proportionally more expensive per level, so this stays a real
#: multiple of MAX_FIELD_POINTS rather than reusing it directly.
MAX_VOLUME_POINTS = 4 * MAX_FIELD_POINTS
#: A real MetPy parcel ascent (`acf.awci.convective_energy.
#: compute_real_cape_cin_at_point()`, called once per real point of
#: `/api/v1/workstation/convection`'s own coarser, strided grid) costs
#: ~5ms/point - this real per-point cost, not MAX_VOLUME_POINTS above
#: (which bounds the pre-stride solver run only), is what must stay
#: responsive over HTTP.
MAX_CONVECTION_POINTS_AFTER_STRIDE = 400


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


def run_complexity_volume(
    model: str,
    steps: int,
    n_lat: int,
    n_lon: int,
    n_levels: int,
    seed: int = 0,
) -> dict[str, Any]:
    """Validate real request-size limits, then genuinely run
    compute_real_complexity_volume() (added 2026-09-04, `/api/v1/
    workstation`) - raises HTTPException(400) rather than letting an
    oversized request hang the server."""
    if model not in MODEL_CONFIGS:
        raise HTTPException(400, f"Unknown model {model!r} - expected one of {sorted(MODEL_CONFIGS)}")
    if n_lat < 1 or n_lon < 1 or n_levels < 1:
        raise HTTPException(400, f"n_lat/n_lon/n_levels must be >= 1, got {n_lat}/{n_lon}/{n_levels}")
    if n_lat * n_lon * n_levels > MAX_VOLUME_POINTS:
        raise HTTPException(
            400,
            f"n_lat*n_lon*n_levels={n_lat * n_lon * n_levels} exceeds this API's real max of "
            f"{MAX_VOLUME_POINTS} volume points per request (protects the server from an unbounded "
            f"real CoupledEarthSolver run over HTTP)",
        )
    if steps < 1 or steps > MAX_STEPS:
        raise HTTPException(400, f"steps must be in [1, {MAX_STEPS}], got {steps}")
    return compute_real_complexity_volume(model=model, steps=steps, n_lat=n_lat, n_lon=n_lon, n_levels=n_levels, seed=seed)


def validate_convection_stride(n_lat: int, n_lon: int, stride: int) -> None:
    """Validate the real post-stride point count `/api/v1/workstation/
    convection` will actually run a real MetPy parcel ascent over -
    raises HTTPException(400) rather than letting an oversized request
    (a small `stride` on a large grid) hang the server. Separate from
    `run_complexity_volume()`'s own pre-stride MAX_VOLUME_POINTS guard,
    which bounds the underlying solver run, not this endpoint's own,
    much more expensive, real per-point parcel-ascent cost."""
    if stride < 1:
        raise HTTPException(400, f"stride must be >= 1, got {stride}")
    n_points_after_stride = math.ceil(n_lat / stride) * math.ceil(n_lon / stride)
    if n_points_after_stride > MAX_CONVECTION_POINTS_AFTER_STRIDE:
        raise HTTPException(
            400,
            f"ceil(n_lat/stride)*ceil(n_lon/stride)={n_points_after_stride} exceeds this API's real max of "
            f"{MAX_CONVECTION_POINTS_AFTER_STRIDE} post-stride points per request (protects the server from "
            f"an unbounded real MetPy parcel-ascent cost over HTTP - increase stride or shrink n_lat/n_lon)",
        )


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
