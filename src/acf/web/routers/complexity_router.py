"""
`/api/v1/complexity` - real HTTP surface over the ACF Complexity Engine
(`acf.awci.calculator.AWCICalculator`, `acf.awci.spatial_field.
compute_real_complexity_field()`).
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, HTTPException

from acf.awci.calculator import AWCICalculator
from acf.web.routers._solver_guard import field_to_json_safe_list, run_complexity_field

router = APIRouter(prefix="/complexity", tags=["complexity"])

#: Every 2D field key compute_real_complexity_field() can genuinely
#: return - see that function's own docstring.
_VALID_FIELD_KEYS = (
    "awci_field",
    "physical_field",
    "forecast_field",
    "temperature_field",
    "wind_speed_field",
    "specific_humidity_field",
    "pressure_field_hpa",
)


@router.post("/score")
async def score(data: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    Real point complexity score - genuinely calls
    `AWCICalculator().calculate(data)`, not a canned response. See that
    method's own docstring for `data`'s real accepted keys
    (temperature, specific_humidity, wind_speed, cape, cin,
    precipitation, pressure, altitude, confidence, temporal_change,
    ensemble_members, model_realizations).
    """
    return AWCICalculator().calculate(data)


@router.get("/field")
async def field(
    model: str = "ARPEGE",
    field_key: str = "awci_field",
    steps: int = 4,
    n_lat: int = 8,
    n_lon: int = 8,
    level: int = 0,
    seed: int = 0,
) -> dict[str, Any]:
    """
    A real 2D complexity field - genuinely runs `CoupledEarthSolver`
    once at `model`'s real grid configuration (see
    `run_complexity_field()`'s own request-size guard) and evaluates
    `AWCICalculator` at every real grid point, same as
    `compute_real_complexity_field()` does everywhere else in this
    project.
    """
    if field_key not in _VALID_FIELD_KEYS:
        raise HTTPException(400, f"Unknown field_key {field_key!r} - expected one of {_VALID_FIELD_KEYS}")
    result = run_complexity_field(model=model, steps=steps, n_lat=n_lat, n_lon=n_lon, level=level, seed=seed)
    return {
        "model": result["model"],
        "lats": result["lats"].tolist(),
        "lons": result["lons"].tolist(),
        "field_key": field_key,
        "field": field_to_json_safe_list(result[field_key]),
        "status": result["status"],
        "is_real_data": result["is_real_data"],
        "honest_limitation": result.get("honest_limitation"),
    }
