"""
`/api/v1/workstation` - real HTTP surface over the ACF Scientific
Workstation's own real per-grid-point diagnostics (added 2026-09-04,
closing the master spec's own disclosed "extension API pour ces
nouveaux modules" follow-up item).

Every endpoint here calls the exact same real, Qt-free functions the
Workstation's own GUI panels use
(`acf.awci.workstation_fields`/`acf.awci.vertical_field.
compute_real_complexity_volume()`) - no new computation is invented,
only a real endpoint exposing what already exists. Same real
request-size guard convention as `complexity_router`/`events_router`/
`datasets_router` (`acf.web.routers._solver_guard`), extended here
with `run_complexity_volume()` for a full (n_levels, n_lat, n_lon)
request.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from acf.awci.workstation_fields import (
    compute_real_theta_e_and_rh_fields,
    compute_real_vorticity_divergence,
    compute_real_wind_shear_field,
)
from acf.web.routers._solver_guard import field_to_json_safe_list, run_complexity_volume

router = APIRouter(prefix="/workstation", tags=["workstation"])


@router.get("/theta_e")
async def theta_e(
    model: str = "ARPEGE",
    steps: int = 4,
    n_lat: int = 8,
    n_lon: int = 8,
    n_levels: int = 4,
    level: int = 0,
    seed: int = 0,
) -> dict[str, Any]:
    """
    Real equivalent potential temperature (θ-e, K) and real relative
    humidity (%) at one real level - genuinely runs `CoupledEarthSolver`
    once at `model`'s real grid configuration (all real levels, see
    `run_complexity_volume()`'s own request-size guard), then calls
    `acf.awci.theta_e.compute_real_theta_e_at_point()` (the CANONICAL,
    published Bolton (1980) formula) at every point of the requested
    real level - same real pipeline the Thermodynamics Lab's own
    auto-rendered θ-e/relative humidity map uses.
    """
    volume = run_complexity_volume(model=model, steps=steps, n_lat=n_lat, n_lon=n_lon, n_levels=n_levels, seed=seed)
    real_level = max(0, min(level, volume["n_levels"] - 1))
    theta_e_field, relative_humidity_field = compute_real_theta_e_and_rh_fields(
        volume["temperature_volume"][real_level],
        volume["specific_humidity_volume"][real_level],
        volume["pressure_volume_hpa"][real_level],
    )
    return {
        "model": volume["model"],
        "level": real_level,
        "lats": volume["lats"].tolist(),
        "lons": volume["lons"].tolist(),
        "theta_e_k": field_to_json_safe_list(theta_e_field),
        "relative_humidity_pct": field_to_json_safe_list(relative_humidity_field),
        "status": "REAL_THETA_E_RELATIVE_HUMIDITY_FROM_ACF_SOLVER",
        "is_real_data": True,
    }


@router.get("/dynamics")
async def dynamics(
    model: str = "ARPEGE",
    steps: int = 4,
    n_lat: int = 8,
    n_lon: int = 8,
    n_levels: int = 4,
    level: int = 0,
    seed: int = 0,
) -> dict[str, Any]:
    """
    Real wind speed (m/s), real relative vorticity (s^-1) and real
    horizontal divergence (s^-1) at one real level - genuinely runs
    `CoupledEarthSolver` once (see `theta_e()`'s own docstring for the
    shared request-size guard), then calls
    `acf.awci.workstation_fields.compute_real_vorticity_divergence()`
    (the standard real metric-spacing gradient approximation feeding
    `VorticityCalculator`/`Divergence` VERBATIM - see that function's
    own docstring) - same real pipeline the Dynamics Lab's own
    Relative vorticity/Divergence map uses. Pole rows are honestly
    non-finite (`null` once JSON-serialized), never a fabricated
    finite value - see `compute_real_vorticity_divergence()`'s own
    docstring for why.
    """
    volume = run_complexity_volume(model=model, steps=steps, n_lat=n_lat, n_lon=n_lon, n_levels=n_levels, seed=seed)
    real_level = max(0, min(level, volume["n_levels"] - 1))
    vorticity_field, divergence_field = compute_real_vorticity_divergence(
        volume["u_volume"][real_level], volume["v_volume"][real_level], volume["lats"], volume["lons"]
    )
    return {
        "model": volume["model"],
        "level": real_level,
        "lats": volume["lats"].tolist(),
        "lons": volume["lons"].tolist(),
        "wind_speed_m_s": field_to_json_safe_list(volume["wind_speed_volume"][real_level]),
        "relative_vorticity_s1": field_to_json_safe_list(vorticity_field),
        "divergence_s1": field_to_json_safe_list(divergence_field),
        "status": "REAL_DYNAMICS_FROM_ACF_SOLVER",
        "is_real_data": True,
    }


@router.get("/wind_shear")
async def wind_shear(
    model: str = "ARPEGE",
    steps: int = 4,
    n_lat: int = 8,
    n_lon: int = 8,
    n_levels: int = 4,
    seed: int = 0,
) -> dict[str, Any]:
    """
    Real bulk wind shear (m/s), full real column (surface to the
    real highest native level - not a fixed physical layer, see
    `compute_real_wind_shear_field()`'s own docstring) - genuinely runs
    `CoupledEarthSolver` once (see `theta_e()`'s own docstring for the
    shared request-size guard). No `level` parameter - a real,
    full-column diagnostic, independent of any single level (same
    convention the Dynamics Lab's own "Bulk wind shear (full column)"
    variable uses).
    """
    volume = run_complexity_volume(model=model, steps=steps, n_lat=n_lat, n_lon=n_lon, n_levels=n_levels, seed=seed)
    shear_field = compute_real_wind_shear_field(volume["u_volume"], volume["v_volume"])
    return {
        "model": volume["model"],
        "lats": volume["lats"].tolist(),
        "lons": volume["lons"].tolist(),
        "wind_shear_m_s": field_to_json_safe_list(shear_field),
        "status": "REAL_WIND_SHEAR_FROM_ACF_SOLVER",
        "is_real_data": True,
    }
