"""
Probabilistic verification of the IFS ENS products against METAR (spec SP5b).

Pairs are exactly those of the deterministic verification (acf.awci.ops.verify.build_pairs, on the
deterministic cube of the same run: nearest cell, METAR within the tolerance, stations too far from the model
surface left out of the ceiling), restricted to the ENS steps. The ENS and deterministic cubes share the IFS
0.25° grid cropped by the same domain; a grid mismatch is an error, never a silent nearest-cell remap.

Events (same definitions as the SP3 verification and the SP5 products):
- ceiling_below_1500ft: observed ceiling_below(METAR, 1500 ft); ENS p_ceiling_1500ft; deterministic ceiling
  below 1500 ft;
- convective: TCU/CB (or TS) observed; ENS p_convection; deterministic convective class >= TCU.

Scores, for N pairs of forecast probability p_k and outcome o_k in {0, 1}:
- Brier score (Brier 1950): BS = (1/N) sum (p_k - o_k)^2;
- fair Brier score (Ferro 2014, Q. J. R. Meteorol. Soc. 140:1917-1923), which removes the penalty of a finite ensemble of m_k
  members: FBS = (1/N) sum [(p_k - o_k)^2 - p_k (1 - p_k) / (m_k - 1)];
- uncertainty UNC = obar (1 - obar), obar the observed frequency; Brier skill score against the sample
  climatology BSS = 1 - BS / UNC (Wilks 2011, Statistical Methods in the Atmospheric Sciences, 3rd ed., ch. 8);
- Murphy (1973, J. Appl. Meteor. 12:595-600) decomposition over the probability bins k: REL = (1/N) sum n_k (pbar_k - obar_k)^2,
  RES = (1/N) sum n_k (obar_k - obar)^2. With binned probabilities BS = REL - RES + UNC only up to the
  within-bin terms (Stephenson, Coelho & Jolliffe 2008, Wea. Forecasting 23:752-757): the residual is reported, never hidden;
- the deterministic forecast of the same run, scored on the same pairs as a probability in {0, 1};
  skill of the ENS against it: 1 - BS_ens / BS_det.

A score whose denominator is zero is null. Pairs are neither independent in space nor in time: no confidence
interval is given, only the sample size and the number of observed events (`sufficient` as in SP3).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import xarray as xr

from acf.awci.obs.metar import ceiling_below
from acf.awci.obs.store import ObsStore
from acf.awci.ops.domains import Domain
from acf.awci.ops.ens_store import EnsStore
from acf.awci.ops.store import CubeStore
from acf.awci.ops.verify import ModelAtStations, Pair, VerifyConfig, build_pairs, model_at_stations

ENS_CEILING_THRESHOLD_FT = 1500  # p_ceiling_1500ft (acf.awci.ops.ensemble.CEILING_1500FT_M)
PROBABILITY_BINS = tuple(np.round(np.linspace(0.0, 1.0, 11), 1))  # 10 bins of 0.1, the last closed
ENS_EVENTS = {"ceiling_below_1500ft": "p_ceiling_1500ft", "convective": "p_convection"}


@dataclass
class EnsAtStations:
    """ENS counts at the stations' cells: arrays (ens step, station), station order of ModelAtStations."""

    steps: list[int]
    missing_steps: list[int]
    count: dict[str, np.ndarray]
    members: dict[str, np.ndarray]


def ens_at_stations(ds: xr.Dataset, manifest: dict[str, Any], model: ModelAtStations,
                    det_lats: np.ndarray, det_lons: np.ndarray) -> EnsAtStations:
    lats, lons = ds["lat"].values, ds["lon"].values
    if lats.shape != det_lats.shape or lons.shape != det_lons.shape or not (
            np.allclose(lats, det_lats) and np.allclose(lons, det_lons)):
        raise ValueError("ENS and deterministic cubes are not on the same grid")
    ii = np.array([int(np.abs(lats - v).argmin()) for v in model.grid_lat], dtype=int)
    jj = np.array([int(np.abs(lons - v).argmin()) for v in model.grid_lon], dtype=int)
    pick = {"lat": xr.DataArray(ii, dims="station"), "lon": xr.DataArray(jj, dims="station")}
    read = lambda name: np.asarray(ds[name].isel(pick).transpose("step", "station").values, dtype=int)  # noqa: E731
    return EnsAtStations(steps=list(manifest["steps"]), missing_steps=list(manifest.get("missing_steps", [])),
                         count={p: read(f"{p}_count") for p in ENS_EVENTS.values()},
                         members={p: read(f"{p}_n") for p in ENS_EVENTS.values()})


@dataclass(frozen=True)
class ProbabilisticSample:
    """One verified case: ENS count of members forecasting the event, members used, outcome, deterministic."""

    event: str
    step: int
    count: int
    members: int
    observed: bool
    deterministic: bool


def ens_samples(pairs: Sequence[Pair], ens: EnsAtStations,
                config: VerifyConfig) -> tuple[list[ProbabilisticSample], dict[str, int]]:
    exclusions = {"not_an_ens_step": 0, "elevation_mismatch": 0, "ceiling_unknown": 0, "convection_unknown": 0,
                  "no_ens_member": 0}
    usable = {s: k for k, s in enumerate(ens.steps) if s not in ens.missing_steps}
    samples: list[ProbabilisticSample] = []
    for p in pairs:
        k = usable.get(p.step)
        if k is None:
            exclusions["not_an_ens_step"] += 1
            continue
        cases: list[tuple[str, bool, bool]] = []
        if p.dz_m is not None and abs(p.dz_m) > config.max_elevation_diff_m:
            exclusions["elevation_mismatch"] += 1
        else:
            observed = ceiling_below(p.obs, ENS_CEILING_THRESHOLD_FT)
            if observed is None:
                exclusions["ceiling_unknown"] += 1
            else:
                det = p.ceiling_ft is not None and p.ceiling_ft < ENS_CEILING_THRESHOLD_FT
                cases.append(("ceiling_below_1500ft", observed, det))
        if p.obs.convective is None or p.model_convective is None:
            exclusions["convection_unknown"] += 1
        else:
            cases.append(("convective", bool(p.obs.convective), bool(p.model_convective)))
        for event, observed, det in cases:
            product = ENS_EVENTS[event]
            m = int(ens.members[product][k, p.n])
            if m == 0:
                exclusions["no_ens_member"] += 1
                continue
            samples.append(ProbabilisticSample(event, p.step, int(ens.count[product][k, p.n]), m, observed, det))
    return samples, exclusions


def _ratio(num: float, den: float) -> float | None:
    return None if den == 0 else float(num / den)


def reliability(p: np.ndarray, o: np.ndarray) -> list[dict[str, Any]]:
    """Reliability diagram and sharpness: per probability bin, cases, mean forecast, observed frequency."""
    edges = np.asarray(PROBABILITY_BINS)
    index = np.clip(np.searchsorted(edges, p, side="right") - 1, 0, len(edges) - 2)
    out = []
    for b in range(len(edges) - 1):
        sel = index == b
        n = int(sel.sum())
        out.append({"lower": float(edges[b]), "upper": float(edges[b + 1]), "n": n,
                    "mean_forecast": float(p[sel].mean()) if n else None,
                    "observed_frequency": float(o[sel].mean()) if n else None})
    return out


def brier_scores(samples: Sequence[ProbabilisticSample], min_observed_events: int = 10) -> dict[str, Any]:
    n = len(samples)
    if n == 0:
        return {"n": 0, "observed_events": 0, "sufficient": False, "brier": None, "fair_brier": None,
                "uncertainty": None, "reliability": None, "resolution": None, "decomposition_residual": None,
                "bss_climatology": None, "brier_deterministic": None, "skill_vs_deterministic": None,
                "diagram": reliability(np.zeros(0), np.zeros(0))}
    count = np.array([s.count for s in samples], dtype=float)
    m = np.array([s.members for s in samples], dtype=float)
    o = np.array([s.observed for s in samples], dtype=float)
    det = np.array([s.deterministic for s in samples], dtype=float)
    p = count / m
    brier = float(np.mean((p - o) ** 2))
    with np.errstate(invalid="ignore", divide="ignore"):
        correction = np.where(m > 1, p * (1 - p) / np.where(m > 1, m - 1, 1), np.nan)
    fair = float(np.mean((p - o) ** 2 - correction)) if np.all(m > 1) else None
    obar = float(o.mean())
    unc = obar * (1 - obar)
    diagram = reliability(p, o)
    rel = sum(b["n"] * (b["mean_forecast"] - b["observed_frequency"]) ** 2 for b in diagram if b["n"]) / n
    res = sum(b["n"] * (b["observed_frequency"] - obar) ** 2 for b in diagram if b["n"]) / n
    brier_det = float(np.mean((det - o) ** 2))
    skill = _ratio(brier, brier_det)
    return {"n": n, "observed_events": int(o.sum()), "sufficient": int(o.sum()) >= min_observed_events,
            "observed_frequency": obar, "mean_probability": float(p.mean()), "brier": brier, "fair_brier": fair,
            "uncertainty": unc, "reliability": float(rel), "resolution": float(res),
            "decomposition_residual": float(brier - (rel - res + unc)),
            "bss_climatology": None if unc == 0 else 1 - brier / unc,
            "brier_deterministic": brier_det, "skill_vs_deterministic": None if skill is None else 1 - skill,
            "members_min": int(m.min()), "members_max": int(m.max()), "diagram": diagram}


def verify_ens_run(samples: Sequence[ProbabilisticSample], exclusions: dict[str, int], config: VerifyConfig,
                   profiles: dict[str, str | None]) -> dict[str, Any]:
    events: dict[str, Any] = {}
    for event in ENS_EVENTS:
        items = [s for s in samples if s.event == event]
        steps = sorted({s.step for s in items})
        events[event] = {"total": brier_scores(items, config.min_observed_events),
                         "by_step": [{"step": st, **{k: v for k, v in brier_scores(
                             [s for s in items if s.step == st], config.min_observed_events).items() if k != "diagram"}}
                             for st in steps]}
    return {
        "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "parameters": config.as_dict() | {"probability_bins": list(PROBABILITY_BINS),
                                          "ceiling_threshold_ft": ENS_CEILING_THRESHOLD_FT},
        "samples": len(samples), "exclusions": exclusions, "events": events,
        # the deterministic reference is like for like only when both used the same cloud profile
        "cloud_profiles": profiles, "like_for_like": profiles.get("ens") == profiles.get("deterministic"),
        "observed": "METAR/SPECI, NOAA/NWS Aviation Weather Center (public domain)",
        "forecast": "AWCI on ECMWF IFS ENS 0.25° (50 perturbed members) and IFS 0.25° (deterministic)",
    }


def run_samples(root: Path, domain: Domain, run: str,
                config: VerifyConfig) -> tuple[list[ProbabilisticSample], dict[str, int], dict[str, str | None]]:
    """Samples of one run from the data directory: deterministic and ENS cubes of the run, METAR archive.
    Raises FileNotFoundError when either cube is absent."""
    cubes, ens_store, obs = CubeStore(root), EnsStore(root), ObsStore(root, domain.name)
    manifest, ds = cubes.manifest(domain.name, run), cubes.dataset(domain.name, run)
    ens_manifest, ens_ds = ens_store.manifest(domain.name, run), ens_store.dataset(domain.name, run)
    stations = obs.stations()
    model = model_at_stations(ds, manifest, stations, domain)
    metars = obs.metars(model.valid_times[0] - timedelta(hours=1), model.valid_times[-1] + timedelta(hours=1))
    pairs, excluded = build_pairs(model, stations, metars, config)
    ens = ens_at_stations(ens_ds, ens_manifest, model, ds["lat"].values, ds["lon"].values)
    samples, exclusions = ens_samples(pairs, ens, config)
    exclusions.update(excluded)
    profiles = {"ens": ens_manifest.get("cloud_profile_version"), "deterministic": manifest.get("cloud_profile_version")}
    return samples, exclusions, profiles
