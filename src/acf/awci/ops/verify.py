"""
Verification of AWCI cloud diagnostics against METAR (spec SP3 §5).

Pairing: the grid cell nearest to each station; at each valid time of the run, the METAR/SPECI closest in
time within `tolerance_min` (ties: routine METAR, then the earlier report). Stations whose elevation
differs from the model surface by more than `max_elevation_diff_m` (HYPOTHESIS, 300 m) are left out of
the ceiling scores (the cell no longer represents the height above the aerodrome) and counted.

Binary events (observed vs forecast):
- ceiling_below_{T}ft, T = 500, 1000, 1500 ft: observed from the METAR (see acf.awci.obs.metar), model
  `ceiling_m` (ICAO ceiling AGL, NaN = none) converted with 1 ft = 0.3048 m;
- convective: TCU or CB observed (or TS), model `convective_class` >= 2 (TCU, Cb calvus, Cb capillatus).

Scores of the 2x2 table (a hits, b false alarms, c misses, d correct negatives, n = a+b+c+d; Jolliffe &
Stephenson 2012, Forecast Verification, 2nd ed., ch. 3):
POD = a/(a+c), FAR = b/(a+b), CSI = a/(a+b+c), frequency bias = (a+b)/(a+c),
ETS = (a - a_r)/(a+b+c - a_r) with a_r = (a+b)(a+c)/n. A score with a zero denominator is null.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

import numpy as np
import xarray as xr

from acf.awci.obs.metar import CEILING_VALUE, MetarError, MetarReport, ceiling_below, parse_metar
from acf.awci.obs.store import parse_time
from acf.awci.ops.domains import Domain

FT_PER_M = 1 / 0.3048
CONVECTIVE_MIN_CLASS = 2  # TCU and above (acf.awci.ops.clouds.CONVECTIVE_CLASSES)
BASE_ERROR_LIMIT_FT = 5000  # METAR layers are only required below 5000 ft (ICAO Annex 3)


@dataclass(frozen=True)
class VerifyConfig:
    tolerance_min: int = 30
    max_elevation_diff_m: float = 300.0
    thresholds_ft: tuple[int, ...] = (500, 1000, 1500)
    lead_bins_h: tuple[tuple[int, int], ...] = ((0, 24), (24, 48), (48, 72))
    min_observed_events: int = 10

    def as_dict(self) -> dict[str, Any]:
        return {"tolerance_min": self.tolerance_min, "max_elevation_diff_m": self.max_elevation_diff_m,
                "thresholds_ft": list(self.thresholds_ft), "lead_bins_h": [list(b) for b in self.lead_bins_h],
                "min_observed_events": self.min_observed_events, "convective_min_class": CONVECTIVE_MIN_CLASS,
                "status": "HYPOTHESIS"}


@dataclass
class ModelAtStations:
    """Model fields at the grid cells nearest to the stations: arrays of shape (step, station)."""

    steps: list[int]
    valid_times: list[datetime]
    missing_steps: list[int]
    icao: list[str]
    grid_lat: list[float]
    grid_lon: list[float]
    ceiling_m: np.ndarray
    convective_class: np.ndarray
    surface_height_m: np.ndarray
    extra: dict[str, np.ndarray] = field(default_factory=dict)  # further fields requested, same (step, station)


@dataclass(frozen=True)
class Pair:
    icao: str
    step: int
    valid_time: datetime
    obs_time: datetime
    obs: MetarReport
    ceiling_ft: float | None  # model; None = no ceiling
    model_convective: bool | None
    dz_m: float | None  # station elevation - model surface height
    k: int = -1  # step index in ModelAtStations
    n: int = -1  # station index in ModelAtStations


def scores(a: int, b: int, c: int, d: int, min_observed_events: int = 10) -> dict[str, Any]:
    n = a + b + c + d
    ratio = lambda num, den: None if den == 0 else num / den  # noqa: E731
    a_r = (a + b) * (a + c) / n if n else 0.0
    return {"a": a, "b": b, "c": c, "d": d, "n": n, "observed_events": a + c, "forecast_events": a + b,
            "pod": ratio(a, a + c), "far": ratio(b, a + b), "csi": ratio(a, a + b + c), "bias": ratio(a + b, a + c),
            "ets": ratio(a - a_r, a + b + c - a_r) if n else None, "sufficient": a + c >= min_observed_events}


def match_reports(records: Sequence[dict[str, Any]], valid_times: Sequence[datetime],
                  tolerance: timedelta) -> list[dict[str, Any] | None]:
    """For each valid time, the report closest in time within the tolerance (ties: METAR, then earlier)."""
    timed = [(parse_time(r["obs_time"]), r) for r in records]
    out: list[dict[str, Any] | None] = []
    for t in valid_times:
        best = min(((abs((ot - t).total_seconds()), r.get("kind") != "METAR", ot, r) for ot, r in timed
                    if abs(ot - t) <= tolerance), key=lambda e: e[:3], default=None)
        out.append(best[3] if best else None)
    return out


def model_at_stations(ds: xr.Dataset, manifest: dict[str, Any], stations: Sequence[dict[str, Any]],
                      domain: Domain, extra_fields: Sequence[str] = ()) -> ModelAtStations:
    inside = [s for s in stations if domain.contains(s["lat"], s["lon"])]
    lats, lons = ds["lat"].values, ds["lon"].values
    ii = np.array([int(np.abs(lats - s["lat"]).argmin()) for s in inside], dtype=int)
    jj = np.array([int(np.abs(lons - s["lon"]).argmin()) for s in inside], dtype=int)
    pick = {"lat": xr.DataArray(ii, dims="station"), "lon": xr.DataArray(jj, dims="station")}
    read = lambda name: np.asarray(ds[name].isel(pick).transpose("step", "station").values, dtype=float)  # noqa: E731
    return ModelAtStations(
        steps=list(manifest["steps"]), valid_times=[parse_time(v) for v in manifest["valid_times"]],
        missing_steps=list(manifest.get("missing_steps", [])), icao=[s["icao"] for s in inside],
        grid_lat=[float(lats[i]) for i in ii], grid_lon=[float(lons[j]) for j in jj],
        ceiling_m=read("ceiling_m"), convective_class=read("convective_class"),
        surface_height_m=read("surface_height_m"), extra={name: read(name) for name in extra_fields},
    )


def _value(x: float) -> float | None:
    return None if np.isnan(x) else float(x)


def build_pairs(model: ModelAtStations, stations: Sequence[dict[str, Any]], metars: Sequence[dict[str, Any]],
                config: VerifyConfig, observed_until: datetime | None = None) -> tuple[list[Pair], dict[str, int]]:
    """Pairs (model, METAR) per station and valid time. Valid times later than `observed_until` (default: the
    latest archived observation) plus the tolerance are counted as `not_yet_observed`, not as missing reports."""
    by_station: dict[str, list[dict[str, Any]]] = {}
    for record in metars:
        by_station.setdefault(record["icao"], []).append(record)
    elevation = {s["icao"]: s.get("elev_m") for s in stations}
    excluded = {"no_report_within_tolerance": 0, "not_yet_observed": 0, "undecodable": 0}
    tolerance = timedelta(minutes=config.tolerance_min)
    if observed_until is None:
        observed_until = max((parse_time(r["obs_time"]) for r in metars), default=datetime.min.replace(tzinfo=UTC))
    usable = [k for k, s in enumerate(model.steps) if s not in model.missing_steps]
    times = [model.valid_times[k] for k in usable]
    pairs: list[Pair] = []
    for n, icao in enumerate(model.icao):
        matched = match_reports(by_station.get(icao, []), times, tolerance)
        for k, match in zip(usable, matched):
            if match is None:
                late = model.valid_times[k] > observed_until + tolerance
                excluded["not_yet_observed" if late else "no_report_within_tolerance"] += 1
                continue
            record = match
            try:
                obs = parse_metar(record["raw"])
            except MetarError:
                excluded["undecodable"] += 1
                continue
            ceiling = _value(model.ceiling_m[k, n])
            cls = _value(model.convective_class[k, n])
            surface = _value(model.surface_height_m[k, n])
            elev = elevation.get(icao)
            pairs.append(Pair(icao, model.steps[k], model.valid_times[k], parse_time(record["obs_time"]), obs,
                              None if ceiling is None else ceiling * FT_PER_M,
                              None if cls is None else cls >= CONVECTIVE_MIN_CLASS,
                              None if elev is None or surface is None else float(elev) - surface, k, n))
    return pairs, excluded


def _lead_label(bounds: tuple[int, int]) -> str:
    return f"{bounds[0]}-{bounds[1]} h"


def _in_bin(step: int, bounds: tuple[int, int], last: bool) -> bool:
    return bounds[0] <= step < bounds[1] or (last and step == bounds[1])


def _table(events: list[tuple[int, bool, bool]], config: VerifyConfig) -> dict[str, Any]:
    def count(items: list[tuple[int, bool, bool]]) -> dict[str, Any]:
        a = sum(o and f for _, o, f in items)
        b = sum(f and not o for _, o, f in items)
        c = sum(o and not f for _, o, f in items)
        d = sum(not o and not f for _, o, f in items)
        return scores(a, b, c, d, config.min_observed_events)

    bins = config.lead_bins_h
    return {"total": count(events),
            "by_lead": [{"lead": _lead_label(b), **count([e for e in events if _in_bin(e[0], b, i == len(bins) - 1)])}
                        for i, b in enumerate(bins)]}


def verify_run(pairs: Sequence[Pair], excluded: dict[str, int], config: VerifyConfig,
               stations_total: int) -> dict[str, Any]:
    exclusions = dict(excluded)
    exclusions.update({"elevation_mismatch": 0, "ceiling_unknown": 0, "convection_unknown": 0})
    events: dict[str, Any] = {}
    elevation_ok = [p for p in pairs if p.dz_m is None or abs(p.dz_m) <= config.max_elevation_diff_m]
    exclusions["elevation_mismatch"] = len(pairs) - len(elevation_ok)
    for threshold in config.thresholds_ft:
        items = []
        for p in elevation_ok:
            observed = ceiling_below(p.obs, threshold)
            if observed is None:
                continue
            items.append((p.step, observed, p.ceiling_ft is not None and p.ceiling_ft < threshold))
        events[f"ceiling_below_{threshold}ft"] = _table(items, config)
    exclusions["ceiling_unknown"] = sum(ceiling_below(p.obs, max(config.thresholds_ft)) is None for p in elevation_ok)
    conv = [(p.step, bool(p.obs.convective), bool(p.model_convective)) for p in pairs
            if p.obs.convective is not None and p.model_convective is not None]
    exclusions["convection_unknown"] = len(pairs) - len(conv)
    events["convective"] = _table(conv, config)
    errors = [p.ceiling_ft - p.obs.ceiling_ft for p in elevation_ok
              if p.obs.ceiling_status == CEILING_VALUE and p.obs.ceiling_ft is not None
              and p.obs.ceiling_ft < BASE_ERROR_LIMIT_FT and p.ceiling_ft is not None
              and p.ceiling_ft < BASE_ERROR_LIMIT_FT]
    return {
        "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "parameters": config.as_dict(),
        "stations": {"total": stations_total, "with_pairs": len({p.icao for p in pairs})},
        "pairs": len(pairs), "exclusions": exclusions, "events": events,
        "ceiling_base_error_ft": {"n": len(errors), "mean_error": float(np.mean(errors)) if errors else None,
                                  "mae": float(np.mean(np.abs(errors))) if errors else None,
                                  "definition": "model - observed, both ceilings below 5000 ft"},
        "observed": "METAR/SPECI, NOAA/NWS Aviation Weather Center (public domain)",
        "forecast": "AWCI cloud diagnostics on ECMWF IFS 0.25° (status HYPOTHESIS)",
    }
