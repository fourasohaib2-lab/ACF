"""
/api/v1/awci - read-only AWCI Web API over the stored cubes (acf.awci.ops.store).

Handlers are plain `def` (FastAPI runs them in its thread pool) and only read
NetCDF slices - no heavy computation per request. Missing values are JSON null.
Every response carries provenance and source_tier "nwp_forecast".
"""

from __future__ import annotations

import math
from typing import Annotated, Any, Literal

import numpy as np
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import Response
from loguru import logger
from pydantic import BaseModel

from acf.awci.ops.domains import Domain
from acf.awci.ops.engine import DEFAULT_OPERATIONAL_PROFILE_PATH, Profile, combine, load_profile
from acf.awci.ops.registry import LAYERS, LEVEL_LAYERS, MODULES, SURFACE_LAYERS
from acf.awci.ops.store import ATTRIBUTION, LICENSE, MODEL, CubeStore

router = APIRouter(prefix="/awci", tags=["awci"])
_MODULES = MODULES
_EXCLUDED = ["temporal", "confidence"]  # not fed in V1 (spec §5.2)
#: Run ids are YYYYMMDDHH only - never a path fragment (path traversal guard).
RunId = Annotated[str, Query(pattern=r"^\d{10}$", description="run id YYYYMMDDHH")]


class Provenance(BaseModel):
    model: str
    run: str
    step: int | None
    valid_time: str | None
    domain: str
    profile: str
    profile_version: str
    license: str
    attribution: str


def _num(value: Any) -> float | None:
    value = float(value)
    return None if math.isnan(value) else value


def _store(request: Request) -> CubeStore:
    return request.app.state.awci_store


def _domain(request: Request, name: str) -> Domain:
    domains: dict[str, Domain] = request.app.state.awci_domains
    if name not in domains:
        raise HTTPException(404, f"unknown domain {name!r}")
    return domains[name]


def _manifest(request: Request, domain: str, run: str) -> dict[str, Any]:
    _domain(request, domain)
    try:
        return _store(request).manifest(domain, run)
    except FileNotFoundError as exc:
        raise HTTPException(404, str(exc)) from exc


def _dataset(request: Request, domain: str, run: str) -> Any:
    try:
        return _store(request).dataset(domain, run)
    except FileNotFoundError as exc:
        raise HTTPException(404, str(exc)) from exc
    except (OSError, ValueError, RuntimeError) as exc:
        logger.error("AWCI cube {}/{} unreadable: {}", domain, run, exc)
        raise HTTPException(503, f"cube {domain}/{run} is unreadable on this server") from exc


def breakdown(module_values: dict[str, float | None], profile: Profile) -> dict[str, Any]:
    """Per-point composite explanation re-derived from the stored module scores (0-1): excluded
    modules, present weight and the decomposition in AWCI points (same formula as engine.combine)."""
    scores: dict[str, np.ndarray | None] = {
        m: (None if m in _EXCLUDED else np.array([np.nan if module_values.get(m) is None else module_values[m]]))
        for m in profile.weights
    }
    result = combine(scores, profile)
    point_missing = [m for m in _MODULES if module_values.get(m) is None]
    decomposition = {
        k: _num(v[0]) for k, v in result.decomposition.items() if k in _MODULES or k in profile.interaction_terms
    }
    return {
        "missing_inputs": point_missing + list(_EXCLUDED),
        "present_weight": float(result.present_weight[0]),
        "decomposition": decomposition,
    }


def _step_index(manifest: dict[str, Any], step: int) -> int:
    if step not in manifest["steps"]:
        raise HTTPException(400, f"step {step} not in this run's steps {manifest['steps']}")
    if step in manifest["missing_steps"]:
        raise HTTPException(404, f"step {step} is missing from this {manifest['status']} run")
    return manifest["steps"].index(step)


def _level_index(manifest: dict[str, Any], level: float) -> int:
    if level not in manifest["levels_hpa"]:
        raise HTTPException(400, f"level {level} hPa not in {manifest['levels_hpa']}")
    return manifest["levels_hpa"].index(level)


def _provenance(manifest: dict[str, Any], step: int | None) -> dict[str, Any]:
    valid = manifest["valid_times"][manifest["steps"].index(step)] if step is not None else None
    return Provenance(model=MODEL, run=manifest["run"], step=step, valid_time=valid, domain=manifest["domain"],
                      profile=manifest["profile"], profile_version=manifest["profile_version"],
                      license=LICENSE, attribution=ATTRIBUTION).model_dump()


def _nearest(ds: Any, domain: Domain, lat: float, lon: float) -> tuple[int, int]:
    if not domain.contains(lat, lon):
        raise HTTPException(400, f"point ({lat}, {lon}) is outside domain {domain.name!r}")
    return int(np.abs(ds["lat"].values - lat).argmin()), int(np.abs(ds["lon"].values - lon).argmin())


def _level_label(profile_thresholds: tuple[tuple[float, str], ...], code: float) -> str | None:
    return None if math.isnan(code) else profile_thresholds[int(code)][1]


@router.get("/domains")
def domains(request: Request) -> list[dict[str, Any]]:
    return [{"name": d.name, "label": d.label, "south": d.south, "north": d.north, "west": d.west, "east": d.east,
             "default": d.default, "resolution_deg": 0.25} for d in request.app.state.awci_domains.values()]


@router.get("/runs")
def runs(request: Request, domain: str) -> list[dict[str, Any]]:
    _domain(request, domain)
    return [{"run": m["run"], "run_time": m["run_time"], "status": m["status"], "steps": m["steps"],
             "missing_steps": m["missing_steps"]} for m in _store(request).runs(domain)]


@router.get("/meta")
def meta(request: Request, domain: str, run: RunId) -> dict[str, Any]:
    m = _manifest(request, domain, run)
    return {"levels_hpa": m["levels_hpa"], "flight_levels": m["flight_levels"], "steps": m["steps"],
            "valid_times": m["valid_times"], "missing_steps": m["missing_steps"], "status": m["status"],
            "level_layers": m["level_layers"], "surface_layers": m["surface_layers"],
            "provenance": _provenance(m, None), "source_tier": "nwp_forecast"}


@router.get("/field", response_model=None)
def field(
    request: Request, domain: str, run: RunId, layer: str, step: int = Query(ge=0, le=384),
    level: float | None = None, format: Literal["json", "f32"] = "json",
) -> dict[str, Any] | Response:
    m = _manifest(request, domain, run)
    if layer not in LEVEL_LAYERS and layer not in SURFACE_LAYERS:
        raise HTTPException(400, f"unknown layer {layer!r}")
    si = _step_index(m, step)
    ds = _dataset(request, domain, run)
    if layer in LEVEL_LAYERS:
        if level is None:
            raise HTTPException(400, f"layer {layer!r} is per-level: 'level' (hPa) is required")
        values = ds[layer].isel(step=si, level=_level_index(m, level)).values
    else:
        values = ds[layer].isel(step=si).values
    lats, lons = ds["lat"].values, ds["lon"].values
    unit = LAYERS[layer].unit if layer in LAYERS else ""
    if format == "f32":
        return Response(
            content=np.ascontiguousarray(values, dtype="<f4").tobytes(), media_type="application/octet-stream",
            headers={"X-AWCI-Shape": f"{values.shape[0]},{values.shape[1]}",
                     "X-AWCI-Lats": f"{lats[0]},{lats[-1]}", "X-AWCI-Lons": f"{lons[0]},{lons[-1]}",
                     "X-AWCI-Nodata": "NaN", "X-AWCI-Unit": unit, "X-AWCI-Attribution": "ECMWF CC-BY-4.0"},
        )
    return {"layer": layer, "unit": unit, "level_hpa": level, "lats": lats.tolist(), "lons": lons.tolist(),
            "values": [[_num(v) for v in row] for row in values],
            "provenance": _provenance(m, step), "source_tier": "nwp_forecast"}


def _column(ds: Any, si: int, i: int, j: int) -> dict[str, np.ndarray]:
    """Every per-level layer at one (step, lat, lon) as a (level,) array - reads only that column's chunks."""
    return {name: ds[name].isel(step=si, lat=i, lon=j).values for name in LEVEL_LAYERS}


def _level_payload(column: dict[str, np.ndarray], li: int, thresholds: Any, profile: Profile) -> dict[str, Any]:
    modules = {m: _num(column[f"module_{m}"][li]) for m in _MODULES}
    level_values = {name: _num(values[li]) for name, values in column.items()
                    if not name.startswith("module_") and name not in ("awci", "awci_level")}
    return {
        "awci": _num(column["awci"][li]),
        "awci_level": _level_label(thresholds, float(column["awci_level"][li])),
        "modules": modules,
        "excluded_modules": list(_EXCLUDED),
        **breakdown(modules, profile),
        "level_layers": level_values,
        "scientific_status": {name: LAYERS[name].status for name in level_values if name in LAYERS}
        | {"awci": LAYERS["awci"].status},
    }


@router.get("/point")
def point(request: Request, domain: str, run: RunId, step: int, level: float, lat: float, lon: float) -> dict[str, Any]:
    m = _manifest(request, domain, run)
    si, li = _step_index(m, step), _level_index(m, level)
    ds = _dataset(request, domain, run)
    i, j = _nearest(ds, _domain(request, domain), lat, lon)
    thresholds = request.app.state.awci_profile.level_thresholds
    return {"lat": float(ds["lat"].values[i]), "lon": float(ds["lon"].values[j]), "level_hpa": level,
            "flight_level": m["flight_levels"][li], **_level_payload(_column(ds, si, i, j), li, thresholds, request.app.state.awci_profile),
            "surface_layers": {name: _num(ds[name].isel(step=si, lat=i, lon=j).values) for name in SURFACE_LAYERS},
            "elevation_m": _num(ds["elevation"].isel(lat=i, lon=j).values),
            "provenance": _provenance(m, step), "source_tier": "nwp_forecast"}


@router.get("/profile")
def profile(request: Request, domain: str, run: RunId, step: int, lat: float, lon: float) -> dict[str, Any]:
    m = _manifest(request, domain, run)
    si = _step_index(m, step)
    ds = _dataset(request, domain, run)
    i, j = _nearest(ds, _domain(request, domain), lat, lon)
    thresholds = request.app.state.awci_profile.level_thresholds
    column = _column(ds, si, i, j)
    levels = [{"level_hpa": p, "flight_level": fl, **_level_payload(column, li, thresholds, request.app.state.awci_profile)}
              for li, (p, fl) in enumerate(zip(m["levels_hpa"], m["flight_levels"]))]
    return {"lat": float(ds["lat"].values[i]), "lon": float(ds["lon"].values[j]), "levels": levels,
            "provenance": _provenance(m, step), "source_tier": "nwp_forecast"}


@router.get("/timeseries")
def timeseries(request: Request, domain: str, run: RunId, level: float, lat: float, lon: float) -> dict[str, Any]:
    m = _manifest(request, domain, run)
    li = _level_index(m, level)
    ds = _dataset(request, domain, run)
    i, j = _nearest(ds, _domain(request, domain), lat, lon)
    prof = request.app.state.awci_profile
    series = ds["awci"].isel(level=li, lat=i, lon=j).values
    module_series = {m: ds[f"module_{m}"].isel(level=li, lat=i, lon=j).values for m in _MODULES}
    points = []
    for si, (s, vt) in enumerate(zip(m["steps"], m["valid_times"])):
        modules = {mod: _num(values[si]) for mod, values in module_series.items()}
        points.append({"step": s, "valid_time": vt, "awci": _num(series[si]), "modules": modules,
                       **breakdown(modules, prof)})
    return {"lat": float(ds["lat"].values[i]), "lon": float(ds["lon"].values[j]), "level_hpa": level,
            "points": points, "provenance": _provenance(m, None), "source_tier": "nwp_forecast"}


@router.get("/registry")
def registry(request: Request) -> dict[str, Any]:
    prof = request.app.state.awci_profile
    classes = [{"upper_bound": None if math.isinf(b) else b, "label": label} for b, label in prof.level_thresholds]
    return {"layers": {name: spec.to_dict() for name, spec in LAYERS.items()}, "classes": classes,
            "profile": {"name": prof.name, "version": prof.version, "weights": prof.weights,
                        "interaction_weights": prof.interaction_weights, "min_present_weight": prof.min_present_weight,
                        "excluded_modules": list(_EXCLUDED)},
            "attribution": ATTRIBUTION, "license": LICENSE}


def default_profile() -> Any:
    return load_profile(DEFAULT_OPERATIONAL_PROFILE_PATH)
