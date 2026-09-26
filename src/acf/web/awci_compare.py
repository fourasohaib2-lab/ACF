"""
IFS-GFS comparison routes of AWCI Web (spec SP6 §4), computed on read from the two deterministic cubes of the same
run (same analysis time) and step (same valid time). Both cubes must share the grid (0.25° cropped by the same
domain): a mismatch is refused, never regridded.

Products:
- awci_diff: AWCI(GFS) - AWCI(IFS), per level, NaN where either is undefined (below the relief, missing module);
- agree_icing (icing potential = 1), agree_cat (Ellrod TI2 category >= moderate), per level, and
  agree_convection (convective class >= TCU), surface: 0 neither model, 1 IFS only, 2 GFS only, 3 both; NaN where
  either model has no value. Events are the ones of the maps and the ensemble (acf.awci.ops.ensemble), no new
  threshold.
"""

from __future__ import annotations

from typing import Annotated, Any

import numpy as np
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import Response

from acf.awci.ops.store import CubeStore
from acf.web.awci_router import RunId, _domain, _nearest, _num

router = APIRouter()
EVENTS: dict[str, tuple[str, float, bool]] = {  # product -> (layer, threshold, per level)
    "agree_icing": ("icing_potential", 1.0, True),
    "agree_cat": ("cat_category", 2.0, True),
    "agree_convection": ("convective_class", 2.0, False),
}
PRODUCTS = ("awci_diff", *EVENTS)
Product = Annotated[str, Query(pattern=r"^(" + "|".join(PRODUCTS) + r")$")]
POINT_LEVEL = ("awci", "icing_potential", "cat_category", "cloud_fraction", "wind_speed", "t", "r")
POINT_SURFACE = ("convective_class", "ceiling_m", "precip_rate", "mucape", "tcc")


def _open(store: CubeStore, model: str, domain: str, run: str, step: int) -> tuple[dict[str, Any], Any, int]:
    try:
        m, ds = store.manifest(domain, run), store.dataset(domain, run)
    except FileNotFoundError as exc:
        raise HTTPException(404, f"no {model.upper()} run {run} for domain {domain!r}: ingest it "
                                 f"(acf-awci-ingest --model {model} --run {run})") from exc
    if step not in m["steps"] or step in m["missing_steps"]:
        raise HTTPException(404, f"step +{step} h is not available in the {model.upper()} run {run}")
    return m, ds, m["steps"].index(step)


def _pair(request: Request, domain: str, run: str, step: int) -> dict[str, tuple[dict[str, Any], Any, int]]:
    d = _domain(request, domain)
    stores: dict[str, CubeStore] = request.app.state.awci_stores
    pair = {model: _open(stores[model], model, d.name, run, step) for model in ("ifs", "gfs")}
    (_, a, _), (_, b, _) = pair["ifs"], pair["gfs"]
    if not (np.array_equal(a["lat"].values, b["lat"].values) and np.array_equal(a["lon"].values, b["lon"].values)):
        raise HTTPException(409, "IFS and GFS cubes are not on the same grid: no comparison (never regridded)")
    return pair


def _level_index(m: dict[str, Any], level: float | None) -> int:
    if level is None or level not in m["levels_hpa"]:
        raise HTTPException(422, f"give a level among {m['levels_hpa']} hPa")
    return int(m["levels_hpa"].index(level))


def agreement(ifs: np.ndarray, gfs: np.ndarray, threshold: float) -> np.ndarray:
    a, b = np.asarray(ifs, dtype=float), np.asarray(gfs, dtype=float)
    with np.errstate(invalid="ignore"):
        code = (a >= threshold).astype(float) + 2.0 * (b >= threshold)
    return np.where(np.isfinite(a) & np.isfinite(b), code, np.nan).astype(np.float32)


@router.get("/compare/field", response_model=None)
def compare_field(request: Request, domain: str, run: RunId, step: int, product: Product,
                  level: float | None = None) -> Response:
    """AWCI difference or hazard agreement between GFS and IFS at one step, float32 (lat, lon) like /field."""
    pair = _pair(request, domain, run, step)
    m, ds, si = pair["ifs"]
    _, gds, gsi = pair["gfs"]
    if product == "awci_diff":
        li = _level_index(m, level)
        values = (gds["awci"].isel(step=gsi, level=li).values - ds["awci"].isel(step=si, level=li).values).astype(np.float32)
        unit = "AWCI points (GFS - IFS)"
    else:
        layer, threshold, per_level = EVENTS[product]
        sel = {"level": _level_index(m, level)} if per_level else {}
        values = agreement(ds[layer].isel(step=si, **sel).values, gds[layer].isel(step=gsi, **sel).values, threshold)
        unit = "0 neither, 1 IFS only, 2 GFS only, 3 both"
    lats, lons = ds["lat"].values, ds["lon"].values
    return Response(content=np.ascontiguousarray(values, dtype="<f4").tobytes(), media_type="application/octet-stream",
                    headers={"X-AWCI-Shape": f"{values.shape[0]},{values.shape[1]}", "X-AWCI-Lats": f"{lats[0]},{lats[-1]}",
                             "X-AWCI-Lons": f"{lons[0]},{lons[-1]}", "X-AWCI-Nodata": "NaN", "X-AWCI-Unit": unit,
                             "X-AWCI-Attribution": "ECMWF CC-BY-4.0; NOAA/NCEP GFS public domain"})


@router.get("/compare/point")
def compare_point(request: Request, domain: str, run: RunId, step: int, level: float, lat: float,
                  lon: float) -> dict[str, Any]:
    """IFS and GFS values at the nearest cell, at the level (per-level layers) and at the surface."""
    pair = _pair(request, domain, run, step)
    m, ds, si = pair["ifs"]
    li = _level_index(m, level)
    i, j = _nearest(ds, _domain(request, domain), lat, lon)
    out: dict[str, Any] = {}
    for model, (mm, mds, msi) in pair.items():
        values = {name: _num(mds[name].isel(step=msi, level=li, lat=i, lon=j).values) for name in POINT_LEVEL}
        values |= {name: _num(mds[name].isel(step=msi, lat=i, lon=j).values) for name in POINT_SURFACE}
        out[model] = {"values": values, "model": mm.get("model"), "attribution": mm.get("attribution"),
                      "cloud_profile_version": mm.get("cloud_profile_version")}
    ifs, gfs = out["ifs"]["values"], out["gfs"]["values"]
    diff = None if ifs["awci"] is None or gfs["awci"] is None else gfs["awci"] - ifs["awci"]
    return {"lat": float(ds["lat"].values[i]), "lon": float(ds["lon"].values[j]), "level_hpa": level, "step": step,
            "run": run, "valid_time": m["valid_times"][si], "models": out, "awci_diff": diff,
            "definition_differences": pair["gfs"][0].get("definition_differences", {})}
