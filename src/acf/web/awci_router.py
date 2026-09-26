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

from acf.awci.ops.cloud_profile import CloudProfile, load_cloud_profile
from acf.awci.ops.clouds import (
    CLEAR,
    CONVECTIVE_CLASSES,
    FT_PER_M,
    GENUS_CODES,
    GENUS_NAMES,
    INDETERMINATE,
    SPECIES_BITS,
    column_layers,
    metar_cloud_group,
)
from acf.awci.ops.domains import Domain
from acf.awci.ops.engine import DEFAULT_OPERATIONAL_PROFILE_PATH, Profile, combine, load_profile
from acf.awci.ops.registry import LAYERS, LEVEL_LAYERS, MODULES, SURFACE_LAYERS
from acf.awci.ops.isa import flight_level
from acf.awci.ops.store import ATTRIBUTION, LICENSE, MODEL, CubeStore
from acf.awci.ops.summary import SUMMARY_THRESHOLDS, area_weights, summarize, weighted_percentile
from acf.awci.ops.thermo import dewpoint_k_from_vapor_pressure, vapor_pressure_hpa

router = APIRouter(prefix="/awci", tags=["awci"])
_MODULES = MODULES
_EXCLUDED = ["temporal", "confidence"]  # not fed in V1 (spec §5.2)
#: Run ids are YYYYMMDDHH only - never a path fragment (path traversal guard).
RunId = Annotated[str, Query(pattern=r"^\d{10}$", description="run id YYYYMMDDHH")]
#: Grid decimation for the 3-D views: every 1st, 2nd or 4th cell.
Stride = Annotated[int, Query(ge=1, le=4, description="grid stride: 1, 2 or 4")]


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


def _run_layers(manifest: dict[str, Any], kind: str) -> tuple[str, ...]:
    """Layers stored in this run (manifest), falling back to the registry when the manifest does not list them."""
    return tuple(manifest.get(kind) or (LEVEL_LAYERS if kind == "level_layers" else SURFACE_LAYERS))


def _require_layer(manifest: dict[str, Any], layer: str) -> None:
    if layer not in _run_layers(manifest, "level_layers") and layer not in _run_layers(manifest, "surface_layers"):
        raise HTTPException(404, f"layer {layer!r} not in run {manifest['run']} (ingested before SP1C?)")


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
             "missing_steps": m["missing_steps"], "ingested_at": m.get("ingested_at")}
            for m in _store(request).runs(domain)]


@router.get("/meta")
def meta(request: Request, domain: str, run: RunId) -> dict[str, Any]:
    m = _manifest(request, domain, run)
    return {"levels_hpa": m["levels_hpa"], "flight_levels": m["flight_levels"], "steps": m["steps"],
            "valid_times": m["valid_times"], "missing_steps": m["missing_steps"], "status": m["status"],
            "level_layers": m["level_layers"], "surface_layers": m["surface_layers"],
            **_cloud_run_info(m), "provenance": _provenance(m, None), "source_tier": "nwp_forecast"}


def _cloud_run_info(m: dict[str, Any]) -> dict[str, Any]:
    """SP1C run-level cloud metadata (None for runs ingested before SP1C)."""
    name = m.get("cloud_profile")
    return {"cloud_status": m.get("cloud_status"), "cloud_consistency": m.get("cloud_consistency"),
            "accumulation_interval_h": m.get("accumulation_interval_h"),
            "cloud_profile": None if name is None else {"name": name, "version": m.get("cloud_profile_version")}}


@router.get("/field", response_model=None)
def field(
    request: Request, domain: str, run: RunId, layer: str, step: int = Query(ge=0, le=384),
    level: float | None = None, format: Literal["json", "f32"] = "json",
) -> dict[str, Any] | Response:
    m = _manifest(request, domain, run)
    if layer not in LEVEL_LAYERS and layer not in SURFACE_LAYERS:
        raise HTTPException(400, f"unknown layer {layer!r}")
    _require_layer(m, layer)
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


def _column(ds: Any, manifest: dict[str, Any], si: int, i: int, j: int) -> dict[str, np.ndarray]:
    """Every per-level layer of this run at one (step, lat, lon) as a (level,) array - reads only that
    column's chunks. Layers are taken from the manifest, so cubes ingested before SP1C stay readable."""
    return {name: ds[name].isel(step=si, lat=i, lon=j).values for name in LEVEL_LAYERS
            if name in _run_layers(manifest, "level_layers")}


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
            "flight_level": m["flight_levels"][li],
            **_level_payload(_column(ds, m, si, i, j), li, thresholds, request.app.state.awci_profile),
            "surface_layers": {name: _num(ds[name].isel(step=si, lat=i, lon=j).values) for name in SURFACE_LAYERS
                               if name in _run_layers(m, "surface_layers")},
            "elevation_m": _num(ds["elevation"].isel(lat=i, lon=j).values),
            "provenance": _provenance(m, step), "source_tier": "nwp_forecast"}


def _dewpoint(column: dict[str, np.ndarray], li: int, p_hpa: float) -> float | None:
    """Td from q and the level pressure (thermo: exact inverse of Bolton e_s), never computed in the browser."""
    q = column.get("q")
    if q is None or not np.isfinite(q[li]):
        return None
    return _num(dewpoint_k_from_vapor_pressure(vapor_pressure_hpa(np.array(q[li]), np.array(p_hpa))))


@router.get("/profile")
def profile(request: Request, domain: str, run: RunId, step: int, lat: float, lon: float) -> dict[str, Any]:
    m = _manifest(request, domain, run)
    si = _step_index(m, step)
    ds = _dataset(request, domain, run)
    i, j = _nearest(ds, _domain(request, domain), lat, lon)
    thresholds = request.app.state.awci_profile.level_thresholds
    column = _column(ds, m, si, i, j)
    levels = [{"level_hpa": p, "flight_level": fl, **_level_payload(column, li, thresholds, request.app.state.awci_profile),
               "dewpoint_k": _dewpoint(column, li, p)}
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
            "cloud_profile": request.app.state.awci_cloud_profile.to_dict(),
            "codes": {"genus": GENUS_CODES, "clear": CLEAR, "indeterminate": INDETERMINATE,
                      "species_bits": SPECIES_BITS, "convective_classes": CONVECTIVE_CLASSES},
            "summary_thresholds": SUMMARY_THRESHOLDS,
            "attribution": ATTRIBUTION, "license": LICENSE}


_CLOUD_SURFACE = ("ceiling_m", "convective_class", "convective_top_m", "convective_top_temp_k", "cloud_top_teff_k",
                  "column_condensate", "tcc", "cloud_cover_bias", "cloud_cover_low", "cloud_cover_mid",
                  "cloud_cover_high", "cloud_cover_total_diag", "genus_low", "genus_mid", "genus_high",
                  "species_flags", "cloud_base_lcl", "sp_hpa", "surface_height_m")


def _genus_name(code: float | None) -> str | None:
    if code is None:
        return None
    return {CLEAR: "clear", INDETERMINATE: "indeterminate"}.get(int(code), GENUS_NAMES.get(int(code)))


@router.get("/clouds")
def clouds(request: Request, domain: str, run: RunId, step: int, lat: float, lon: float) -> dict[str, Any]:
    """Cloud layers at a point: probable genus and species, base/top, oktas, ICAO ceiling, convection,
    model METAR-style cloud group. Model diagnostics (status HYPOTHESIS), never observations."""
    m = _manifest(request, domain, run)
    _require_layer(m, "cloud_fraction")
    si = _step_index(m, step)
    ds = _dataset(request, domain, run)
    i, j = _nearest(ds, _domain(request, domain), lat, lon)
    col = {name: ds[name].isel(step=si, lat=i, lon=j).values
           for name in ("cloud_fraction", "cloud_genus", "cloud_species", "gh")}
    sfc = {name: _num(ds[name].isel(step=si, lat=i, lon=j).values) for name in _CLOUD_SURFACE}
    elevation = sfc["surface_height_m"] or 0.0  # sea level over sea (SRTM15+ elevation carries bathymetry)
    cloud_profile: CloudProfile = request.app.state.awci_cloud_profile
    nan = float("nan")
    layers = column_layers(
        np.asarray(m["levels_hpa"], dtype=float), col["cloud_fraction"], col["cloud_genus"], col["gh"], elevation,
        sfc["sp_hpa"] if sfc["sp_hpa"] is not None else nan,
        col["cloud_species"],
        sfc["convective_class"] if sfc["convective_class"] is not None else nan,
        sfc["convective_top_m"] if sfc["convective_top_m"] is not None else nan,
        sfc["cloud_base_lcl"] if sfc["cloud_base_lcl"] is not None else nan, cloud_profile,
    )
    ceiling = sfc["ceiling_m"]
    cls = int(sfc["convective_class"] or 0)
    names = ("cloud_fraction", "cloud_genus", "ceiling_m", "convective_class", "species_flags", "cloud_top_teff_k",
             "column_condensate", "cloud_cover_total_diag")
    return {
        "lat": float(ds["lat"].values[i]), "lon": float(ds["lon"].values[j]), "elevation_m": elevation,
        "layers": layers, "metar": "MODEL " + metar_cloud_group(layers),
        "etage_bounds_fl": None if sfc["sp_hpa"] is None else {
            "low_mid": flight_level(cloud_profile.sigma_low_mid * sfc["sp_hpa"]),
            "mid_high": flight_level(cloud_profile.sigma_mid_high * sfc["sp_hpa"])},
        "ceiling_m": ceiling, "ceiling_ft": None if ceiling is None else int(ceiling * FT_PER_M),
        "convective": {"class": cls, "label": CONVECTIVE_CLASSES[cls], "top_m": sfc["convective_top_m"],
                       "top_temp_k": sfc["convective_top_temp_k"]},
        "cloud_top_teff_k": sfc["cloud_top_teff_k"], "column_condensate": sfc["column_condensate"],
        "tcc": sfc["tcc"], "cloud_cover_bias": sfc["cloud_cover_bias"],
        "cloud_covers": {"low": sfc["cloud_cover_low"], "mid": sfc["cloud_cover_mid"],
                         "high": sfc["cloud_cover_high"], "total_diag": sfc["cloud_cover_total_diag"]},
        "genus": {e: _genus_name(sfc[f"genus_{e}"]) for e in ("low", "mid", "high")},
        "scientific_status": {name: LAYERS[name].status for name in names},
        "cloud_profile": {"name": m.get("cloud_profile", cloud_profile.name),
                          "version": m.get("cloud_profile_version", cloud_profile.version)},
        "run_cloud_status": m.get("cloud_status"),
        "step_consistency": next((c for c in m.get("cloud_consistency") or [] if c["step"] == step), None),
        "accumulation_interval_h": (m.get("accumulation_interval_h") or [None] * len(m["steps"]))[si],
        "provenance": _provenance(m, step), "source_tier": "nwp_forecast",
    }


_SUMMARY_LEVEL = ("awci", "cat_category", "icing_potential", "vertical_shear")
_SUMMARY_SURFACE = ("mucape", "precip_class", "ceiling_m", "convective_class", "cloud_cover_bias")


def _summary_layers(ds: Any, m: dict[str, Any], si: int, li: int) -> dict[str, np.ndarray | None]:
    surface = _run_layers(m, "surface_layers")
    out: dict[str, np.ndarray | None] = {n: ds[n].isel(step=si, level=li).values for n in _SUMMARY_LEVEL}
    out |= {n: ds[n].isel(step=si).values if n in surface else None for n in _SUMMARY_SURFACE}
    return out


@router.get("/summary")
def summary(request: Request, domain: str, run: RunId, level: float,
            step: int = Query(ge=0, le=384)) -> dict[str, Any]:
    m = _manifest(request, domain, run)
    si, li = _step_index(m, step), _level_index(m, level)
    ds = _dataset(request, domain, run)
    lats = ds["lat"].values
    body = summarize(_summary_layers(ds, m, si, li), lats, request.app.state.awci_profile)
    awci_all = ds["awci"].isel(step=si).values
    w = area_weights(lats, awci_all.shape[2])
    body["awci_p95_by_level"] = [{"level_hpa": p, "flight_level": fl, "awci_p95": weighted_percentile(awci_all[k], w, 95.0)}
                                 for k, (p, fl) in enumerate(zip(m["levels_hpa"], m["flight_levels"]))]
    return body | {"level_hpa": level, "provenance": _provenance(m, step), "source_tier": "nwp_forecast"}


@router.get("/summary/series")
def summary_series(request: Request, domain: str, run: RunId, level: float) -> dict[str, Any]:
    m = _manifest(request, domain, run)
    li = _level_index(m, level)
    ds = _dataset(request, domain, run)
    lats, prof = ds["lat"].values, request.app.state.awci_profile
    points = []
    for si, (s, vt) in enumerate(zip(m["steps"], m["valid_times"])):
        if s in m["missing_steps"]:
            points.append({"step": s, "valid_time": vt, "missing": True})
            continue
        body = summarize(_summary_layers(ds, m, si, li), lats, prof)
        points.append({"step": s, "valid_time": vt, "missing": False,
                       **{k: body[k] for k in ("awci_p95", "turbulence_area_pct", "icing_area_pct",
                                               "convection_area_pct", "cb_area_pct")}})
    return {"level_hpa": level, "points": points, "provenance": _provenance(m, None), "source_tier": "nwp_forecast"}


@router.get("/clouds/series")
def clouds_series(request: Request, domain: str, run: RunId, lat: float, lon: float) -> dict[str, Any]:
    """Per-step etage genus, convection and ceiling at a point: temporal variability of the cloud diagnosis."""
    m = _manifest(request, domain, run)
    _require_layer(m, "genus_low")
    ds = _dataset(request, domain, run)
    i, j = _nearest(ds, _domain(request, domain), lat, lon)
    names = ("genus_low", "genus_mid", "genus_high", "convective_class", "ceiling_m", "cloud_cover_total_diag")
    series = {n: ds[n].isel(lat=i, lon=j).values for n in names}
    points = []
    for si, (s, vt) in enumerate(zip(m["steps"], m["valid_times"])):
        if s in m["missing_steps"]:
            points.append({"step": s, "valid_time": vt, "missing": True})
            continue
        points.append({"step": s, "valid_time": vt, "missing": False,
                       "genus": {e: _genus_name(_num(series[f"genus_{e}"][si])) for e in ("low", "mid", "high")},
                       "convective_class": _num(series["convective_class"][si]),
                       "ceiling_m": _num(series["ceiling_m"][si]),
                       "cloud_cover_total_diag": _num(series["cloud_cover_total_diag"][si])})
    return {"lat": float(ds["lat"].values[i]), "lon": float(ds["lon"].values[j]), "points": points,
            "provenance": _provenance(m, None), "source_tier": "nwp_forecast"}


def _grid_headers(lats: np.ndarray, lons: np.ndarray, unit: str) -> dict[str, str]:
    return {"X-AWCI-Lats": f"{lats[0]},{lats[-1]}", "X-AWCI-Lons": f"{lons[0]},{lons[-1]}",
            "X-AWCI-Nodata": "NaN", "X-AWCI-Unit": unit, "X-AWCI-Attribution": "ECMWF CC-BY-4.0"}


def _check_stride(stride: int) -> None:
    if stride not in (1, 2, 4):
        raise HTTPException(422, f"stride must be 1, 2 or 4, got {stride}")


@router.get("/volume", response_model=None)
def volume(request: Request, domain: str, run: RunId, layer: str, step: int = Query(ge=0, le=384),
           stride: Stride = 1) -> Response:
    """3-D field for the volume view: float32 values (level, lat, lon) followed by gh on the same grid."""
    _check_stride(stride)
    m = _manifest(request, domain, run)
    if layer not in LEVEL_LAYERS:
        raise HTTPException(400, f"layer {layer!r} is not a per-level layer")
    _require_layer(m, layer)
    si = _step_index(m, step)
    ds = _dataset(request, domain, run)
    values = ds[layer].isel(step=si).values[:, ::stride, ::stride]
    gh = ds["gh"].isel(step=si).values[:, ::stride, ::stride]
    lats, lons = ds["lat"].values[::stride], ds["lon"].values[::stride]
    body = np.ascontiguousarray(values, dtype="<f4").tobytes() + np.ascontiguousarray(gh, dtype="<f4").tobytes()
    unit = LAYERS[layer].unit if layer in LAYERS else ""
    return Response(content=body, media_type="application/octet-stream", headers={
        "X-AWCI-Shape": ",".join(str(n) for n in values.shape), "X-AWCI-Parts": "values,gh",
        "X-AWCI-Levels": ",".join(f"{p:g}" for p in m["levels_hpa"]), **_grid_headers(lats, lons, unit)})


@router.get("/terrain", response_model=None)
def terrain(request: Request, domain: str, run: RunId, stride: Stride = 1) -> Response:
    """IFS model surface height (m AMSL, hypsometric from surface pressure: acf.awci.ops.thermo.model_surface_height_m)
    of the run's grid, float32 (lat, lon). Runs ingested before SP1C have no surface_height_m: 404."""
    _check_stride(stride)
    m = _manifest(request, domain, run)
    _require_layer(m, "surface_height_m")
    ds = _dataset(request, domain, run)
    first = next(si for si, s in enumerate(m["steps"]) if s not in m["missing_steps"])
    values = ds["surface_height_m"].isel(step=first).values[::stride, ::stride]
    lats, lons = ds["lat"].values[::stride], ds["lon"].values[::stride]
    return Response(content=np.ascontiguousarray(values, dtype="<f4").tobytes(),
                    media_type="application/octet-stream",
                    headers={"X-AWCI-Shape": f"{values.shape[0]},{values.shape[1]}", **_grid_headers(lats, lons, "m")})


def default_profile() -> Any:
    return load_profile(DEFAULT_OPERATIONAL_PROFILE_PATH)


def default_cloud_profile() -> CloudProfile:
    return load_cloud_profile()


# Observation overlays (EUMETView relay) share the /awci prefix and every app that mounts this router.
from acf.web.awci_wms import router as _wms_router  # noqa: E402

router.include_router(_wms_router)

# Aeronautical observations (METAR/TAF/SIGMET, verification) read from the acf-awci-obs store.
from acf.web.awci_obs import router as _obs_router  # noqa: E402

router.include_router(_obs_router)

# IFS ENS probabilities and spread (SP5), read from the acf-awci-ens store.
from acf.web.awci_ens import router as _ens_router  # noqa: E402

router.include_router(_ens_router)

from acf.web.awci_route import router as _route_router  # noqa: E402

router.include_router(_route_router)
