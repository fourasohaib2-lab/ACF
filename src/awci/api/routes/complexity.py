"""
`/complexity` - real HTTP surface over
``awci.complexity.calculator.AWCICalculator`` - the ``routes/
complexity.py`` module named in
``docs/architecture/awci_reference_architecture.md`` section 18
("API").

A real, AWCI-native sibling of ``acf.web.routers.complexity_router``
(which serves the same real ``AWCICalculator`` engine, round-tripped
through the ``acf.awci`` backward-compatible shim, at ACF's own
general-purpose FastAPI app) - this one imports ``awci.complexity``
directly rather than via that shim, matching this session's own
"repoint real dependents to the new location directly" discipline
already applied throughout the AWCI package migration.

``/field`` and ``/vertical-profile`` (added for the AWCI web
dashboard's GlobalMap/RegionalMap and VerticalCrossSection panels) are
thin HTTP wrappers over 2 already-real, already-tested engines -
``awci.complexity.spatial_field.compute_real_complexity_field()``
(Complexity(x, y), genuinely runs ``CoupledEarthSolver`` once and
evaluates ``AWCICalculator`` at every real grid point) and
``awci.complexity.vertical_field.compute_real_complexity_volume()`` +
``vertical_profile_at_point()`` (Complexity(x, y, z), same real solver
run extended to every native level, then a real nearest-grid-point
column extraction) - no new physics, no new formula, and no synthetic
fallback is added here. Both real engines' own extensive
``honest_limitation`` disclosure is passed straight through unedited
so the frontend can surface it rather than imply a more complete
field than what was actually computed (see each engine's own module
docstring for the full, real scope: no terrain/orography, no real
precipitation field, ``forecast_field``/``forecast_profile`` stay flat
under default weights - re-running the ensemble/multi-model fusion at
every grid point does not scale with today's infrastructure).
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np
from fastapi import APIRouter, Body, HTTPException

from awci.complexity.calculator import AWCICalculator
from awci.complexity.spatial_field import compute_real_complexity_field
from awci.complexity.vertical_field import compute_real_complexity_volume, vertical_profile_at_point

router = APIRouter(prefix="/complexity", tags=["complexity"])


def _to_json_safe_numeric(value: Any) -> Any:
    """
    Real, JSON-safe conversion for the numpy-heavy return values of
    ``spatial_field``/``vertical_field`` - not a duplicate of
    ``acf.utils.serialization.to_json_safe`` (that module stays
    numpy-free, matching this project's "avoid unnecessary
    dependencies" rule for a utility every caller pulls in; only the 2
    real physics-field routes below actually need numpy-array
    handling). ``numpy.ndarray`` becomes a nested list
    (``.tolist()``), ``numpy.floating``/``numpy.integer`` becomes a
    plain Python number, and any real ``NaN`` (genuinely present
    wherever the underlying engine honestly could not compute a value
    - see each engine's own ``np.nan``-not-fabricated-0.0 discipline)
    becomes JSON ``null`` rather than the non-standard, often-rejected
    literal ``NaN`` token. Dicts/lists/tuples are walked recursively;
    everything else is returned unchanged.
    """
    if isinstance(value, np.ndarray):
        return _to_json_safe_numeric(value.tolist())
    if isinstance(value, (np.floating,)):
        f = float(value)
        return None if math.isnan(f) else f
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, dict):
        return {key: _to_json_safe_numeric(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_json_safe_numeric(item) for item in value]
    return value


@router.post("/score")
async def score(data: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    Real point complexity score - genuinely calls
    ``AWCICalculator().calculate(data)``, not a canned response. See
    that method's own docstring for ``data``'s real accepted keys
    (temperature, specific_humidity, wind_speed, cape, cin,
    precipitation, pressure, altitude, confidence, temporal_change,
    ensemble_members, model_realizations).
    """
    return AWCICalculator().calculate(data)


@router.get("/field")
async def field(
    model: str = "ARPEGE",
    level: int = 0,
    steps: int = 8,
    seed: int = 0,
    n_lat: int | None = None,
    n_lon: int | None = None,
) -> dict[str, Any]:
    """
    Real 2D Complexity(x, y) field for the dashboard's GlobalMap/
    RegionalMap panels - genuinely calls
    ``compute_real_complexity_field()`` (runs ``CoupledEarthSolver``
    once at ``model``'s real grid configuration, then evaluates
    ``AWCICalculator`` at every real grid point), not a synthetic
    pattern. ``n_lat``/``n_lon`` override the model's default
    resolution (e.g. for a faster, coarser field) - omit for
    ``model``'s real default grid.
    """
    try:
        result = compute_real_complexity_field(
            model=model, steps=steps, seed=seed, level=level, n_lat=n_lat, n_lon=n_lon
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return _to_json_safe_numeric(
        {
            "lats": result["lats"],
            "lons": result["lons"],
            "model": result["model"],
            "level": result["level"],
            "awci_field": result["awci_field"],
            "physical_field": result["physical_field"],
            "forecast_field": result["forecast_field"],
            "module_fields": result["module_fields"],
            "status": result["status"],
            "is_real_data": result["is_real_data"],
            "honest_limitation": result["honest_limitation"],
        }
    )


@router.get("/vertical-profile")
async def vertical_profile(
    lat: float,
    lon: float,
    model: str = "ARPEGE",
    steps: int = 8,
    seed: int = 0,
    n_lat: int | None = None,
    n_lon: int | None = None,
    n_levels: int | None = None,
) -> dict[str, Any]:
    """
    Real Complexity(z) vertical profile at the real grid column
    nearest (``lat``, ``lon``), for the dashboard's
    VerticalCrossSection panel - genuinely calls
    ``compute_real_complexity_volume()`` (the same real
    ``CoupledEarthSolver`` run extended to every native vertical
    level) then ``vertical_profile_at_point()`` (a real nearest-
    neighbour column extraction, not spatial interpolation). Ordered
    surface (index 0) to top of atmosphere - see
    ``vertical_field.py``'s own module docstring for why these are the
    solver's real NATIVE levels (each with its own real local
    pressure in ``pressure_profile_hpa``), not standard pressure
    levels.
    """
    try:
        volume = compute_real_complexity_volume(
            model=model, steps=steps, seed=seed, n_lat=n_lat, n_lon=n_lon, n_levels=n_levels
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    profile = vertical_profile_at_point(volume, lat, lon)
    return _to_json_safe_numeric(
        {
            **profile,
            "model": volume["model"],
            "n_levels": volume["n_levels"],
            "status": volume["status"],
            "is_real_data": volume["is_real_data"],
            "honest_limitation": volume["honest_limitation"],
        }
    )
