"""
Evaluate ceiling-base variants against METAR, out of sample (evidence for docs/awci/AWCI_WEB_SP3.md).

    .venv/bin/python tools/awci/evaluate_ceiling_base.py --data-dir DIR --domain north_africa \
        --train 2026092300,2026092312,2026092400,2026092412 --test 2026092500,2026092512,2026092600

Variants of the model ceiling (ICAO ceiling layer found by acf.awci.ops.clouds):
- level: base at the height of the lowest BKN/OVC level (current diagnosis);
- lcl_in_level: the surface-parcel LCL (Bolton) replaces it when it lies within the vertical interval the
  level represents (well-mixed boundary layer: cloud base at the LCL, Stull 1988);
- lcl_clip: the LCL clipped into that interval.
Pairs as in acf.awci.ops.verify (nearest cell, METAR +-30 min, |dz| <= 300 m), steps 0-24 h.
"""

from __future__ import annotations

import argparse
import sys
from datetime import timedelta
from pathlib import Path

import numpy as np
import xarray as xr

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from acf.awci.obs.metar import CEILING_VALUE, MetarReport, ceiling_below  # noqa: E402
from acf.awci.obs.store import ObsStore  # noqa: E402
from acf.awci.ops.clouds import level_interfaces  # noqa: E402
from acf.awci.ops.domains import DEFAULT_DOMAINS_PATH, load_domains  # noqa: E402
from acf.awci.ops.store import CubeStore  # noqa: E402
from acf.awci.ops.verify import VerifyConfig, build_pairs, model_at_stations, scores  # noqa: E402

FT_PER_M = 1 / 0.3048
VARIANTS = ("level", "lcl_in_level", "lcl_clip")
MAX_STEP_H = 24
MAX_DZ_M = 300.0


def refined_ceiling_m(ceiling_m: float, gh_column: np.ndarray, elevation: float, lcl_agl_m: float,
                      variant: str) -> float:
    """Ceiling (m AGL) under a variant; NaN stays NaN (no ceiling)."""
    if variant == "level" or not np.isfinite(ceiling_m) or not np.isfinite(lcl_agl_m):
        return ceiling_m
    lower, upper = level_interfaces(np.asarray(gh_column, float)[:, None, None], np.array([[elevation]]))
    k = int(np.argmin(np.abs(np.asarray(gh_column) - elevation - ceiling_m)))
    lo, hi = float(lower[k, 0, 0]) - elevation, float(upper[k, 0, 0]) - elevation
    if variant == "lcl_in_level":
        return lcl_agl_m if lo <= lcl_agl_m <= hi else ceiling_m
    return float(np.clip(lcl_agl_m, lo, hi))


def run_items(root: Path, domain_name: str, run: str) -> list[tuple[MetarReport, dict[str, float]]]:
    domain = load_domains(DEFAULT_DOMAINS_PATH)[domain_name]
    cubes, obs = CubeStore(root), ObsStore(root, domain_name)
    stations = obs.stations()
    manifest, ds = cubes.manifest(domain_name, run), cubes.dataset(domain_name, run)
    model = model_at_stations(ds, manifest, stations, domain, extra_fields=("cloud_base_lcl",))
    inside = [s for s in stations if domain.contains(s["lat"], s["lon"])]
    ii = xr.DataArray([int(np.abs(ds["lat"].values - s["lat"]).argmin()) for s in inside], dims="station")
    jj = xr.DataArray([int(np.abs(ds["lon"].values - s["lon"]).argmin()) for s in inside], dims="station")
    gh = ds["gh"].isel(lat=ii, lon=jj).transpose("step", "level", "station").values
    metars = obs.metars(model.valid_times[0] - timedelta(hours=1), model.valid_times[-1] + timedelta(hours=1))
    pairs, _ = build_pairs(model, stations, metars, VerifyConfig())
    items = []
    for p in pairs:
        if p.step > MAX_STEP_H or (p.dz_m is not None and abs(p.dz_m) > MAX_DZ_M):
            continue
        ceiling_m = np.nan if p.ceiling_ft is None else p.ceiling_ft / FT_PER_M
        values = {v: refined_ceiling_m(ceiling_m, gh[p.k, :, p.n], float(model.surface_height_m[p.k, p.n]),
                                       float(model.extra["cloud_base_lcl"][p.k, p.n]), v) * FT_PER_M
                  for v in VARIANTS}
        items.append((p.obs, values))
    return items


def evaluate(items: list[tuple[MetarReport, dict[str, float]]], variant: str) -> dict[str, object]:
    out: dict[str, object] = {}
    for threshold in (500, 1000, 1500):
        a = b = c = d = 0
        for obs, values in items:
            observed = ceiling_below(obs, threshold)
            if observed is None:
                continue
            forecast = bool(np.isfinite(values[variant]) and values[variant] < threshold)
            a += observed and forecast
            b += forecast and not observed
            c += observed and not forecast
            d += not observed and not forecast
        out[f"below_{threshold}ft"] = scores(a, b, c, d)
    errors = [values[variant] - obs.ceiling_ft for obs, values in items
              if obs.ceiling_status == CEILING_VALUE and obs.ceiling_ft is not None and obs.ceiling_ft < 5000
              and np.isfinite(values[variant]) and values[variant] < 5000]
    out["base_error_ft"] = {"n": len(errors), "mean": float(np.mean(errors)) if errors else None,
                            "mae": float(np.mean(np.abs(errors))) if errors else None}
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--domain", default="north_africa")
    parser.add_argument("--train", required=True)
    parser.add_argument("--test", required=True)
    args = parser.parse_args(argv)
    for label, runs in (("calibration", args.train.split(",")), ("test", args.test.split(","))):
        items = [i for r in runs for i in run_items(args.data_dir, args.domain, r)]
        print(f"{label} ({len(items)} pairs)")
        for variant in VARIANTS:
            res = evaluate(items, variant)
            cells = [f"<{t} ft bias {res[f'below_{t}ft']['bias']:.2f} ETS {res[f'below_{t}ft']['ets']:.3f}"  # type: ignore[index]
                     for t in (500, 1000, 1500)]
            err = res["base_error_ft"]
            print(f"  {variant:13s} " + " | ".join(cells) + f" | base ME {err['mean']:.0f} ft n {err['n']}")  # type: ignore[index]
    return 0


if __name__ == "__main__":
    sys.exit(main())
