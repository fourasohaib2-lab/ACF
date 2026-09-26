"""
Route routes of AWCI Web (spec SP4 §3): vertical cross-section along a great-circle route, and route meteogram.

Samples every 10 km (acf.awci.ops.route); each sample takes the value of its nearest grid cell, as the
inspector does: nothing is interpolated. A route leaving the domain is refused.

Meteogram, per step and level, over the route samples holding a finite value (samples below the model surface
are not counted): AWCI maximum and median; fraction of the route in class >= High (lower bound of the
operational profile's High class), in icing potential, in CAT >= moderate (Ellrod TI2 category >= 2), in cloud
>= 5/8 (BKN, WMO code table 2700). Samples are equally spaced, so a fraction of samples is a fraction of
distance. Thresholds are ACF's own (acf.awci.ops.ensemble), none is new.
"""

from __future__ import annotations

import warnings
from typing import Annotated, Any

import numpy as np
import xarray as xr
from fastapi import APIRouter, HTTPException, Query, Request

from acf.awci.ops.ensemble import BKN_FRACTION, class_lower_bound
from acf.awci.ops.registry import LAYERS, LEVEL_LAYERS
from acf.awci.ops.route import RouteError, RouteSamples, parse_points, sample_route
from acf.web.awci_router import RunId, _dataset, _domain, _manifest, _num, _provenance, _require_layer, _step_index

router = APIRouter()
Points = Annotated[str, Query(max_length=600, description="lat,lon;lat,lon;… (2 to 20 points)")]
SPACING_KM = 10.0


def _samples(request: Request, domain: str, points: str) -> RouteSamples:
    try:
        route = sample_route(parse_points(points), SPACING_KM)
    except RouteError as exc:
        raise HTTPException(400, str(exc)) from exc
    d = _domain(request, domain)
    outside = [k for k, (la, lo) in enumerate(zip(route.lat, route.lon)) if not d.contains(float(la), float(lo))]
    if outside:
        k = outside[0]
        raise HTTPException(400, f"the route leaves domain {domain!r} at {route.distance_km[k]:.0f} km "
                                 f"({route.lat[k]:.2f}, {route.lon[k]:.2f})")
    return route


def _cells(ds: Any, route: RouteSamples) -> dict[str, xr.DataArray]:
    ii = np.abs(ds["lat"].values[:, None] - route.lat[None, :]).argmin(axis=0)
    jj = np.abs(ds["lon"].values[:, None] - route.lon[None, :]).argmin(axis=0)
    return {"lat": xr.DataArray(ii, dims="sample"), "lon": xr.DataArray(jj, dims="sample")}


def _nums(values: np.ndarray) -> list[Any]:
    return [_nums(v) if np.ndim(v) else _num(v) for v in values]


def _route_payload(route: RouteSamples, ds: Any, pick: dict[str, xr.DataArray]) -> dict[str, Any]:
    return {
        "length_km": route.length_km, "spacing_km": SPACING_KM,
        "distance_km": np.round(route.distance_km, 2).tolist(),
        "lat": np.round(route.lat, 4).tolist(), "lon": np.round(route.lon, 4).tolist(),
        "grid_lat": ds["lat"].values[pick["lat"].values].tolist(), "grid_lon": ds["lon"].values[pick["lon"].values].tolist(),
        "waypoints": [{"index": k, "distance_km": float(route.distance_km[k]), "lat": float(route.lat[k]),
                       "lon": float(route.lon[k])} for k in route.waypoint_index],
    }


@router.get("/route/section")
def route_section(request: Request, domain: str, run: RunId, step: int, layer: str, points: Points) -> dict[str, Any]:
    """Vertical cross-section of a per-level layer along the route at one step (values: level x sample)."""
    m = _manifest(request, domain, run)
    if layer not in LEVEL_LAYERS:
        raise HTTPException(400, f"layer {layer!r} is not a per-level layer")
    _require_layer(m, layer)
    si = _step_index(m, step)
    route = _samples(request, domain, points)
    ds = _dataset(request, domain, run)
    pick = _cells(ds, route)
    values = ds[layer].isel(step=si, **pick).transpose("level", "sample").values
    surface = {name: _nums(ds[name].isel(step=si, **pick).values) if name in ds else None
               for name in ("sp_hpa", "surface_height_m")}
    return {
        **_route_payload(route, ds, pick), "layer": layer, "unit": LAYERS[layer].unit if layer in LAYERS else "",
        "levels_hpa": m["levels_hpa"], "flight_levels": m["flight_levels"], "values": _nums(values),
        "surface_pressure_hpa": surface["sp_hpa"], "surface_height_m": surface["surface_height_m"],
        "provenance": _provenance(m, step), "source_tier": "nwp_forecast",
    }


def _fraction(event: np.ndarray, valid: np.ndarray) -> list[float | None]:
    n = valid.sum(axis=-1)
    with np.errstate(invalid="ignore", divide="ignore"):
        frac = np.where(n > 0, (event & valid).sum(axis=-1) / np.where(n > 0, n, 1), np.nan)
    return _nums(frac)


@router.get("/route/meteogram")
def route_meteogram(request: Request, domain: str, run: RunId, points: Points) -> dict[str, Any]:
    """Per step and level: AWCI max/median and hazard fractions along the route (definitions: module doc)."""
    m = _manifest(request, domain, run)
    route = _samples(request, domain, points)
    ds = _dataset(request, domain, run)
    pick = _cells(ds, route)
    read = lambda name: ds[name].isel(**pick).transpose("step", "level", "sample").values  # noqa: E731
    awci, icing, cat, cloud = read("awci"), read("icing_potential"), read("cat_category"), read("cloud_fraction")
    high = class_lower_bound(request.app.state.awci_profile, "High")
    with np.errstate(invalid="ignore"), warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)  # all-NaN slice (level under the relief all along) -> NaN
        awci_max, awci_median = np.nanmax(awci, axis=-1), np.nanmedian(awci, axis=-1)
        fields = {
            "awci_max": _nums(awci_max), "awci_median": _nums(awci_median),
            "frac_awci_high": _fraction(awci >= high, np.isfinite(awci)),
            "frac_icing": _fraction(icing >= 1, np.isfinite(icing)),
            "frac_cat_moderate": _fraction(cat >= 2, np.isfinite(cat)),
            "frac_cloud_bkn": _fraction(cloud >= BKN_FRACTION, np.isfinite(cloud)),
        }
    steps = []
    for si, (step, vt) in enumerate(zip(m["steps"], m["valid_times"])):
        missing = step in m["missing_steps"]
        steps.append({"step": step, "valid_time": vt, "missing": missing,
                      **{k: None if missing else v[si] for k, v in fields.items()}})
    return {**_route_payload(route, ds, pick), "levels_hpa": m["levels_hpa"], "flight_levels": m["flight_levels"],
            "awci_high_lower_bound": high, "steps": steps, "provenance": _provenance(m, None),
            "source_tier": "nwp_forecast"}
