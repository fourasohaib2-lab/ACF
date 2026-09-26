"""
IFS ENS routes of AWCI Web (spec SP5 §4): runs, manifest, probability/statistic fields, point series.

Probabilities are derived on read from the stored exact counts: count / n, NaN where n = 0 (no member held a
finite value, or the step was not computed). Nothing is interpolated between ENS steps.
"""

from __future__ import annotations

from typing import Annotated, Any

import numpy as np
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import Response

from acf.awci.ops.domains import Domain
from acf.awci.ops.ens_store import EnsStore
from acf.awci.ops.ensemble import ENS_LEVEL_PRODUCTS, ENS_STATISTICS, ENS_SURFACE_PRODUCTS

router = APIRouter()
RunId = Annotated[str, Query(pattern=r"^\d{10}$")]
Product = Annotated[str, Query(pattern=r"^(" + "|".join((*ENS_LEVEL_PRODUCTS, *ENS_SURFACE_PRODUCTS, *ENS_STATISTICS)) + r")$")]


def _store(request: Request) -> EnsStore:
    return EnsStore(request.app.state.awci_store.root)


def _domain(request: Request, name: str) -> Domain:
    domain = request.app.state.awci_domains.get(name)
    if domain is None:
        raise HTTPException(404, f"unknown domain {name!r}")
    return domain


def _manifest(request: Request, domain: str, run: str) -> dict[str, Any]:
    try:
        return _store(request).manifest(_domain(request, domain).name, run)
    except FileNotFoundError as exc:
        raise HTTPException(404, str(exc)) from exc


def _step_index(m: dict[str, Any], step: int) -> int:
    if step not in m["steps"] or step in m["missing_steps"]:
        raise HTTPException(404, f"ENS step +{step} h is not available for run {m['run']} (steps {m['steps']}, "
                                 f"missing {m['missing_steps']})")
    return int(m["steps"].index(step))


def _probability(count: np.ndarray, n: np.ndarray) -> np.ndarray:
    count, n = count.astype(np.float32), n.astype(np.float32)
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(n > 0, count / np.where(n > 0, n, 1), np.nan).astype(np.float32)


@router.get("/ens/runs")
def ens_runs(request: Request, domain: str) -> list[dict[str, Any]]:
    keys = ("run", "run_time", "status", "steps", "missing_steps", "members_used", "ingested_at")
    return [{k: m.get(k) for k in keys} for m in _store(request).runs(_domain(request, domain).name)]


@router.get("/ens/meta")
def ens_meta(request: Request, domain: str, run: RunId) -> dict[str, Any]:
    return _manifest(request, domain, run)


@router.get("/ens/field", response_model=None)
def ens_field(request: Request, domain: str, run: RunId, product: Product, step: int, level: float | None = None) -> Response:
    """Probability (0-1) of an ENS product, or AWCI mean/spread, float32 (lat, lon) like /field?format=f32."""
    m = _manifest(request, domain, run)
    si = _step_index(m, step)
    per_level = product not in ENS_SURFACE_PRODUCTS
    if per_level and level is None:
        raise HTTPException(422, f"{product} is defined per level: give level (hPa)")
    ds = _store(request).dataset(domain, run)
    sel: dict[str, int] = {"step": si}
    if per_level:
        levels = [float(v) for v in ds["level"].values]
        if float(level or 0) not in levels:
            raise HTTPException(404, f"level {level} hPa not in {levels}")
        sel["level"] = levels.index(float(level or 0))
    if product in ENS_STATISTICS:
        values, unit = ds[product].isel(sel).values.astype(np.float32), "AWCI (0-100)"
    else:
        values = _probability(ds[f"{product}_count"].isel(sel).values, ds[f"{product}_n"].isel(sel).values)
        unit = "probability"
    lats, lons = ds["lat"].values, ds["lon"].values
    return Response(content=np.ascontiguousarray(values, dtype="<f4").tobytes(), media_type="application/octet-stream",
                    headers={"X-AWCI-Shape": f"{values.shape[0]},{values.shape[1]}", "X-AWCI-Lats": f"{lats[0]},{lats[-1]}",
                             "X-AWCI-Lons": f"{lons[0]},{lons[-1]}", "X-AWCI-Nodata": "NaN", "X-AWCI-Unit": unit,
                             "X-AWCI-Members": str(m["members_used"].get(str(step), 0)),
                             "X-AWCI-Attribution": "ECMWF CC-BY-4.0 IFS ENS"})


def _num(x: float) -> float | None:
    return None if not np.isfinite(x) else float(x)


@router.get("/ens/point")
def ens_point(request: Request, domain: str, run: RunId, lat: float, lon: float, level: float) -> dict[str, Any]:
    """Every product and the AWCI spread per ENS step at a point and level (surface products ignore the level)."""
    d = _domain(request, domain)
    if not d.contains(lat, lon):
        raise HTTPException(400, f"point ({lat}, {lon}) is outside domain {domain!r}")
    m = _manifest(request, domain, run)
    ds = _store(request).dataset(domain, run)
    levels = [float(v) for v in ds["level"].values]
    if float(level) not in levels:
        raise HTTPException(404, f"level {level} hPa not in {levels}")
    li = levels.index(float(level))
    i, j = int(np.abs(ds["lat"].values - lat).argmin()), int(np.abs(ds["lon"].values - lon).argmin())
    points = []
    for si, (step, vt) in enumerate(zip(m["steps"], m["valid_times"])):
        if step in m["missing_steps"]:
            points.append({"step": step, "valid_time": vt, "missing": True, "members": 0, "probabilities": None,
                           "awci_mean": None, "awci_std": None})
            continue
        probs: dict[str, float | None] = {}
        for product in (*ENS_LEVEL_PRODUCTS, *ENS_SURFACE_PRODUCTS):
            sel = {"step": si, "lat": i, "lon": j} | ({"level": li} if product in ENS_LEVEL_PRODUCTS else {})
            n = int(ds[f"{product}_n"].isel(sel).values)
            probs[product] = None if n == 0 else int(ds[f"{product}_count"].isel(sel).values) / n
        stat = {"step": si, "level": li, "lat": i, "lon": j}
        points.append({"step": step, "valid_time": vt, "missing": False, "members": m["members_used"].get(str(step), 0),
                       "probabilities": probs, "awci_mean": _num(float(ds["awci_mean"].isel(stat).values)),
                       "awci_std": _num(float(ds["awci_std"].isel(stat).values))})
    return {"lat": float(ds["lat"].values[i]), "lon": float(ds["lon"].values[j]), "level_hpa": level, "points": points,
            "run": m["run"], "members_requested": len(m["members_requested"]), "attribution": m["attribution"]}
