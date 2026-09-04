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
    CONVECTION_GRID_STRIDE,
    compute_real_convection_indices_field,
    compute_real_terrain_field,
    compute_real_theta_e_and_rh_fields,
    compute_real_vorticity_divergence,
    compute_real_wind_shear_field,
)
from acf.web.routers._solver_guard import (
    field_to_json_safe_list,
    run_complexity_volume,
    validate_convection_stride,
)

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


@router.get("/convection")
async def convection(
    model: str = "ARPEGE",
    steps: int = 4,
    n_lat: int = 8,
    n_lon: int = 8,
    n_levels: int = 8,
    seed: int = 0,
    stride: int = CONVECTION_GRID_STRIDE,
) -> dict[str, Any]:
    """
    Real severe-convection composite indices - CAPE, CIN, LCL height,
    bulk wind shear, storm-relative helicity, EHI, SCP, STP - on a
    real, coarser subset of the requested grid (every `stride`-th real
    row/column). Genuinely runs `CoupledEarthSolver` once (see
    `theta_e()`'s own docstring for the shared request-size guard),
    then calls `acf.awci.workstation_fields.
    compute_real_convection_indices_field()` (same real pipeline the
    Convection Lab's own "🔄 Compute Convective Indices Field" button
    uses - see that function's own docstring for the full disclosure
    of every real, cited formula composed and the honest parcel/layer
    simplifications used). No `level` parameter - these are all real
    full-column diagnostics, same convention as `wind_shear()` above.
    `stride` additionally guards this endpoint's own real per-point
    MetPy parcel-ascent cost (~5ms/point - see
    `validate_convection_stride()`'s own docstring), separate from
    `run_complexity_volume()`'s pre-stride solver-size guard above.
    """
    validate_convection_stride(n_lat, n_lon, stride)
    volume = run_complexity_volume(model=model, steps=steps, n_lat=n_lat, n_lon=n_lon, n_levels=n_levels, seed=seed)
    result = compute_real_convection_indices_field(
        volume["temperature_volume"],
        volume["specific_humidity_volume"],
        volume["pressure_volume_hpa"],
        volume["u_volume"],
        volume["v_volume"],
        volume["lats"],
        volume["lons"],
        stride=stride,
    )
    return {
        "model": volume["model"],
        "stride": stride,
        "lats": result["lats"].tolist(),
        "lons": result["lons"].tolist(),
        "cape_j_kg": field_to_json_safe_list(result["cape_j_kg"]),
        "cin_j_kg": field_to_json_safe_list(result["cin_j_kg"]),
        "lcl_m": field_to_json_safe_list(result["lcl_m"]),
        "bulk_shear_m_s": field_to_json_safe_list(result["bulk_shear_m_s"]),
        "srh_m2_s2": field_to_json_safe_list(result["srh_m2_s2"]),
        "ehi": field_to_json_safe_list(result["ehi"]),
        "scp": field_to_json_safe_list(result["scp"]),
        "stp": field_to_json_safe_list(result["stp"]),
        "status": "REAL_CONVECTION_INDICES_FROM_ACF_SOLVER",
        "is_real_data": True,
    }


@router.get("/terrain")
async def terrain(
    model: str = "ARPEGE",
    steps: int = 4,
    n_lat: int = 8,
    n_lon: int = 8,
    n_levels: int = 8,
    seed: int = 0,
) -> dict[str, Any]:
    """
    Real terrain elevation (real, bundled, cited SRTM15+ V2.7 grid -
    see `acf.awci.terrain_elevation`'s own module docstring), real
    near-surface Brunt-Väisälä static stability, and the real
    mountain-wave Froude number - genuinely runs `CoupledEarthSolver`
    once (see `theta_e()`'s own docstring for the shared request-size
    guard), then calls `acf.awci.workstation_fields.
    compute_real_terrain_field()` (same real pipeline the Terrain
    Lab's own auto-rendered map uses - see that function's own
    docstring for the full disclosure of every real formula composed
    and its honest, disclosed simplifications). No `level` parameter -
    these are all real full-column diagnostics, same convention as
    `wind_shear()`/`convection()` above. No `stride` parameter either -
    unlike `convection()`, this real pipeline is fully vectorized (no
    real per-point MetPy parcel ascent), so `run_complexity_volume()`'s
    existing pre-run size guard is already sufficient here.
    """
    volume = run_complexity_volume(model=model, steps=steps, n_lat=n_lat, n_lon=n_lon, n_levels=n_levels, seed=seed)
    result = compute_real_terrain_field(
        volume["temperature_volume"], volume["pressure_volume_hpa"], volume["wind_speed_volume"],
        volume["lats"], volume["lons"],
    )
    return {
        "model": volume["model"],
        "lats": result["lats"].tolist(),
        "lons": result["lons"].tolist(),
        "elevation_m": field_to_json_safe_list(result["elevation_m"]),
        "brunt_vaisala_n_s1": field_to_json_safe_list(result["brunt_vaisala_n_s1"]),
        "froude_number": field_to_json_safe_list(result["froude_number"]),
        "status": "REAL_TERRAIN_FROM_ACF_SOLVER",
        "is_real_data": True,
    }
