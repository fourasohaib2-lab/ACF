"""
Aeronautical observation routes of AWCI Web (spec SP3 §6): aerodromes with the METAR nearest to a time,
aerodrome detail against the model, international SIGMETs valid at a time, verification report.

Observations are read from the store filled by `acf-awci-obs`; no request ever reaches the AWC from here.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any

import numpy as np
from fastapi import APIRouter, HTTPException, Query, Request

from acf.awci.obs.metar import MetarError, MetarReport, parse_metar
from acf.awci.obs.store import ObsStore, parse_time
from acf.awci.ops.clouds import CLEAR, GENUS_NAMES, INDETERMINATE
from acf.awci.ops.domains import Domain
from acf.awci.ops.store import CubeStore
from acf.awci.ops.verify import VerifyConfig, build_pairs, match_reports, model_at_stations, verify_run

ATTRIBUTION = "Aviation Weather Center, NOAA/NWS — domaine public"
TOLERANCE = timedelta(minutes=30)
FT_PER_M = 1 / 0.3048

router = APIRouter()
Icao = Annotated[str, Query(pattern=r"^[A-Z][A-Z0-9]{3}$")]
RunId = Annotated[str, Query(pattern=r"^\d{10}$")]


def _cubes(request: Request) -> CubeStore:
    return request.app.state.awci_store


def _domain(request: Request, name: str) -> Domain:
    domain = request.app.state.awci_domains.get(name)
    if domain is None:
        raise HTTPException(404, f"unknown domain {name!r}")
    return domain


def _obs(request: Request, domain: str) -> ObsStore:
    return ObsStore(_cubes(request).root, _domain(request, domain).name)


def _time(value: str | None) -> datetime:
    if value is None:
        return datetime.now(UTC)
    try:
        return parse_time(value)
    except ValueError as exc:
        raise HTTPException(422, "time must be ISO-8601, e.g. 2026-09-25T03:00:00Z") from exc


def _fmt(t: datetime) -> str:
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def _num(value: float) -> float | None:
    return None if np.isnan(value) else float(value)


def decoded(record: dict[str, Any]) -> dict[str, Any] | None:
    """A stored METAR record with its decoded observation (None when the text is not decodable)."""
    try:
        r: MetarReport = parse_metar(record["raw"])
    except MetarError:
        return None
    return {"time": record["obs_time"], "kind": record.get("kind", r.kind), "raw": record["raw"], "auto": r.auto,
            "visibility_m": r.visibility_m, "weather": list(r.weather), "cavok": r.cavok, "no_sig_cloud": r.no_sig_cloud,
            "layers": [{"cover": x.cover, "base_ft": x.base_ft, "type": x.cloud_type} for x in r.layers],
            "vertical_visibility_ft": r.vertical_visibility_ft, "ceiling_status": r.ceiling_status,
            "ceiling_ft": r.ceiling_ft, "convective": r.convective, "flight_category": r.flight_category}


@router.get("/airports")
def airports(request: Request, domain: str, time: str | None = None) -> dict[str, Any]:
    """METAR stations of the domain with the report nearest to `time` (±30 min; default now)."""
    store = _obs(request, domain)
    when = _time(time)
    stations = store.stations()
    metars = store.metars(when - TOLERANCE, when + TOLERANCE)
    by_station: dict[str, list[dict[str, Any]]] = {}
    for record in metars:
        by_station.setdefault(record["icao"], []).append(record)
    out = []
    for s in stations:
        match = match_reports(by_station.get(s["icao"], []), [when], TOLERANCE)[0]
        out.append({**s, "observation": decoded(match) if match else None})
    status = store.status()
    return {"time": _fmt(when), "tolerance_min": 30, "airports": out, "ingested_at": status.get("ingested_at"),
            "attribution": ATTRIBUTION, "flight_category_definition": "FAA (affichage)"}


def _station(store: ObsStore, icao: str) -> dict[str, Any]:
    station = next((s for s in store.stations() if s["icao"] == icao), None)
    if station is None:
        raise HTTPException(404, f"no METAR station {icao!r} in this domain")
    return station


def _genus(code: float) -> str | None:
    if np.isnan(code):
        return None
    return {CLEAR: "clear", INDETERMINATE: "indeterminate"}.get(int(code), GENUS_NAMES.get(int(code)))


@router.get("/airport")
def airport(request: Request, domain: str, icao: Icao, run: RunId) -> dict[str, Any]:
    """One aerodrome over a run: METAR of the run window, latest TAF, model series and matched pairs."""
    d = _domain(request, domain)
    store = _obs(request, domain)
    station = _station(store, icao)
    try:
        manifest = _cubes(request).manifest(d.name, run)
        ds = _cubes(request).dataset(d.name, run)
    except FileNotFoundError as exc:
        raise HTTPException(404, str(exc)) from exc
    model = model_at_stations(ds, manifest, [station], d)
    if not model.icao:
        raise HTTPException(404, f"{icao} lies outside domain {domain!r}")
    i = int(np.abs(ds["lat"].values - station["lat"]).argmin())
    j = int(np.abs(ds["lon"].values - station["lon"]).argmin())
    genus_low = ds["genus_low"].isel(lat=i, lon=j).values if "genus_low" in ds else None
    cover_low = ds["cloud_cover_low"].isel(lat=i, lon=j).values if "cloud_cover_low" in ds else None
    series = []
    for k, (step, vt) in enumerate(zip(model.steps, model.valid_times)):
        ceiling = _num(model.ceiling_m[k, 0])
        series.append({"step": step, "valid_time": _fmt(vt), "missing": step in model.missing_steps,
                       "ceiling_ft": None if ceiling is None else ceiling * FT_PER_M,
                       "convective_class": _num(model.convective_class[k, 0]),
                       "surface_height_m": _num(model.surface_height_m[k, 0]),
                       "genus_low": None if genus_low is None else _genus(float(genus_low[k])),
                       "cloud_cover_low": None if cover_low is None else _num(float(cover_low[k]))})
    window = (model.valid_times[0] - timedelta(hours=1), model.valid_times[-1] + timedelta(hours=1))
    metars = [m for m in store.metars(*window) if m["icao"] == icao]
    pairs, _ = build_pairs(model, [station], metars, VerifyConfig())
    taf = next((t for t in store.tafs() if t["icao"] == icao), None)
    surface = series[0]["surface_height_m"]
    return {
        "station": station, "grid": {"lat": model.grid_lat[0], "lon": model.grid_lon[0]},
        "dz_m": None if surface is None else station["elev_m"] - surface,
        "metars": [x for x in map(decoded, metars) if x], "taf": taf, "model": series,
        "pairs": [{"step": p.step, "valid_time": _fmt(p.valid_time),
                   "observation": decoded({"obs_time": _fmt(p.obs_time), "raw": p.obs.raw, "kind": p.obs.kind}),
                   "model_ceiling_ft": p.ceiling_ft, "model_convective": p.model_convective} for p in pairs],
        "run": run, "attribution": ATTRIBUTION, "model_attribution": manifest.get("attribution"),
    }


@router.get("/sigmets")
def sigmets(request: Request, domain: str, time: str | None = None) -> dict[str, Any]:
    """International SIGMETs valid at `time` (default now) crossing the domain, as GeoJSON."""
    store = _obs(request, domain)
    when = _time(time)
    features = []
    for s in store.sigmets_at(when):
        ring = [list(c) for c in s["coords"]]
        if ring[0] != ring[-1]:
            ring.append(ring[0])
        props = {k: v for k, v in s.items() if k != "coords"}
        features.append({"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [ring]}, "properties": props})
    return {"type": "FeatureCollection", "features": features, "time": _fmt(when),
            "ingested_at": store.status().get("ingested_at"), "attribution": ATTRIBUTION}


@lru_cache(maxsize=16)
def _verification(root: str, domain: Domain, run: str, cube_mtime: float, obs_mtime: float) -> str:
    cubes, store = CubeStore(Path(root)), ObsStore(root, domain.name)
    manifest = cubes.manifest(domain.name, run)
    model = model_at_stations(cubes.dataset(domain.name, run), manifest, store.stations(), domain)
    first, last = model.valid_times[0], model.valid_times[-1]
    metars = store.metars(first - timedelta(hours=1), last + timedelta(hours=1))
    config = VerifyConfig()
    pairs, excluded = build_pairs(model, store.stations(), metars, config)
    report = verify_run(pairs, excluded, config, stations_total=len(store.stations()))
    report.update({"domain": domain.name, "run": run, "valid_from": _fmt(first), "valid_to": _fmt(last),
                   "observations_ingested_at": store.status().get("ingested_at")})
    return json.dumps(report)


@router.get("/verification")
def verification(request: Request, domain: str, run: RunId) -> dict[str, Any]:
    """Verification of the run's ceiling and convection against METAR (cached until cube or archive change)."""
    d = _domain(request, domain)
    cubes = _cubes(request)
    cube = cubes.root / d.name / run / "cube.nc"
    if not cube.exists():
        raise HTTPException(404, f"no run {run!r} for domain {domain!r}")
    store = ObsStore(cubes.root, d.name)
    report: dict[str, Any] = json.loads(_verification(str(cubes.root), d, run, cube.stat().st_mtime, store.mtime()))
    return report
