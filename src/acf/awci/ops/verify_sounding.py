"""
Verification of the model column against radiosondes (spec SP7 §3-4).

Pairing: a sounding of nominal time T (00/12 UTC) against the run's step valid at T; the grid cell nearest to the
launch position (balloon drift, tens of km aloft, neglected); only the pressure levels reported exactly in the
profile (no vertical interpolation), and only where the model has a value (levels below the model surface are NaN).

Per level and in total, model - observation:
- temperature T (K); relative humidity over water (%): model from q, T, p (acf.awci.ops.thermo.relative_humidity_pct,
  capped at 100 %), observation as reported over water (University of Wyoming);
- wind: speed bias and vector RMSE sqrt(du^2 + dv^2), observed (u, v) = (-V sin dd, -V cos dd);
- vertical wind shear |dV|/dz between neighbouring levels, the model definition (acf.awci.ops.kinematics.layer_shear)
  applied to the observed profile with its geopotential heights;
- icing potential: contingency table (Jolliffe & Stephenson 2012) against the same ACF diagnostic applied to the
  observed profile (acf.awci.ops.hazards.icing_potential): a check of the diagnostic's inputs, not an observation of
  icing, which no open source provides over the domain. Ellrod's CAT index needs the horizontal deformation, which a
  sounding does not measure: only its vertical-shear factor is verified.

Bias = mean(model - obs), RMSE = sqrt(mean((model - obs)^2)), n = number of level pairs; null when n = 0.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import numpy as np
import xarray as xr

from acf.awci.obs.sounding import ATTRIBUTION, wind_components
from acf.awci.obs.store import parse_time
from acf.awci.ops.domains import Domain
from acf.awci.ops.hazards import icing_potential
from acf.awci.ops.kinematics import layer_shear
from acf.awci.ops.thermo import relative_humidity_pct
from acf.awci.ops.verify import scores

KELVIN = 273.15
VARIABLES = ("t", "rh", "wind_speed", "vws")


@dataclass
class ColumnPair:
    """One sounding against the model column: arrays over the run's levels (NaN where either side is missing)."""

    wmo: str
    name: str
    step: int
    valid_time: str
    levels_hpa: np.ndarray
    model: dict[str, np.ndarray]
    obs: dict[str, np.ndarray]


def _obs_columns(record: dict[str, Any], levels: np.ndarray) -> dict[str, np.ndarray]:
    by_p = {float(lv["p_hpa"]): lv for lv in record["levels"]}
    get = lambda key: np.array([by_p.get(float(p), {}).get(key) for p in levels], dtype=float)  # noqa: E731
    t_k, rh, z = get("t_c") + KELVIN, get("rh_pct"), get("z_m")
    speed, direction = get("wspd_ms"), get("wdir_deg")
    uv = [wind_components(s, d) if np.isfinite(s) and np.isfinite(d) else (np.nan, np.nan)
          for s, d in zip(speed, direction)]
    u, v = np.array([a for a, _ in uv]), np.array([b for _, b in uv])
    _, vws = layer_shear(u[:, None], v[:, None], z[:, None])
    return {"t": t_k, "rh": rh, "u": u, "v": v, "wind_speed": speed, "vws": vws[:, 0],
            "icing": icing_potential(t_k, rh)}


def column_pairs(ds: xr.Dataset, manifest: dict[str, Any], soundings: Sequence[dict[str, Any]],
                 domain: Domain) -> tuple[list[ColumnPair], dict[str, int]]:
    excluded = {"no_step_at_nominal_time": 0, "outside_domain": 0}
    valid = {parse_time(vt): k for k, (s, vt) in enumerate(zip(manifest["steps"], manifest["valid_times"]))
             if s not in manifest.get("missing_steps", [])}
    levels = np.asarray(manifest["levels_hpa"], dtype=float)
    lats, lons = ds["lat"].values, ds["lon"].values
    pairs = []
    for record in soundings:
        k = valid.get(parse_time(record["nominal_time"]))
        if k is None:
            excluded["no_step_at_nominal_time"] += 1
            continue
        lat, lon = record.get("lat"), record.get("lon")
        if lat is None or lon is None or not domain.contains(lat, lon):
            excluded["outside_domain"] += 1
            continue
        i, j = int(np.abs(lats - lat).argmin()), int(np.abs(lons - lon).argmin())
        col = lambda name: np.asarray(ds[name].isel(step=k, lat=i, lon=j).values, dtype=float)  # noqa: E731
        t, q, u, v = col("t"), col("q"), col("u"), col("v")
        model = {"t": t, "rh": relative_humidity_pct(t, q, levels), "u": u, "v": v, "wind_speed": np.hypot(u, v),
                 "vws": col("vertical_shear"), "icing": col("icing_potential")}
        pairs.append(ColumnPair(record["wmo"], str(record.get("name", "")), manifest["steps"][k],
                                manifest["valid_times"][k], levels, model, _obs_columns(record, levels)))
    return pairs, excluded


def _continuous(diff: np.ndarray) -> dict[str, Any]:
    d = diff[np.isfinite(diff)]
    return {"n": int(d.size), "bias": float(d.mean()) if d.size else None,
            "rmse": float(np.sqrt(np.mean(d**2))) if d.size else None}


def _vector_rmse(du: np.ndarray, dv: np.ndarray) -> float | None:
    ok = np.isfinite(du) & np.isfinite(dv)
    return float(np.sqrt(np.mean(du[ok] ** 2 + dv[ok] ** 2))) if ok.any() else None


def _stack(pairs: Sequence[ColumnPair], side: str, name: str, n_levels: int) -> np.ndarray:
    return np.stack([getattr(p, side)[name] for p in pairs]) if pairs else np.zeros((0, n_levels))


def verify_soundings(pairs: Sequence[ColumnPair], excluded: dict[str, int], levels_hpa: Sequence[float],
                     min_observed_events: int = 10) -> dict[str, Any]:
    n = len(levels_hpa)
    diff = {v: _stack(pairs, "model", v, n) - _stack(pairs, "obs", v, n) for v in VARIABLES}
    du = _stack(pairs, "model", "u", n) - _stack(pairs, "obs", "u", n)
    dv = _stack(pairs, "model", "v", n) - _stack(pairs, "obs", "v", n)
    mi, oi = _stack(pairs, "model", "icing", n), _stack(pairs, "obs", "icing", n)

    def icing(sel: Any) -> dict[str, Any]:
        m, o = mi[sel], oi[sel]
        ok = np.isfinite(m) & np.isfinite(o)
        m, o = m[ok] >= 1, o[ok] >= 1
        return scores(int((m & o).sum()), int((m & ~o).sum()), int((~m & o).sum()), int((~m & ~o).sum()),
                      min_observed_events)

    per_level = []
    for li, p in enumerate(levels_hpa):
        sel = (slice(None), li)
        per_level.append({"level_hpa": float(p), **{v: _continuous(diff[v][sel]) for v in VARIABLES},
                          "wind_vector_rmse": _vector_rmse(du[sel], dv[sel]), "icing": icing(sel)})
    everything = (slice(None), slice(None))
    return {
        "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "soundings": len(pairs), "stations": len({p.wmo for p in pairs}), "exclusions": excluded,
        "levels": per_level,
        "total": {**{v: _continuous(diff[v].ravel()) for v in VARIABLES},
                  "wind_vector_rmse": _vector_rmse(du.ravel(), dv.ravel()), "icing": icing(everything)},
        "units": {"t": "K", "rh": "%", "wind_speed": "m/s", "vws": "1/s", "wind_vector_rmse": "m/s"},
        "definitions": "model - observation; icing reference = ACF diagnostic on the observed profile (status HYPOTHESIS)",
        "observed": ATTRIBUTION,
    }
