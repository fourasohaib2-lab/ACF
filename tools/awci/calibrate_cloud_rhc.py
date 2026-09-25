"""
Calibrate the critical relative humidities of the cloud profile against IFS tcc on stored cubes.

    .venv/bin/python tools/awci/calibrate_cloud_rhc.py --domain north_africa --runs 2026092506 \
        [--steps 0-72/6] [--data-dir DIR] [--profile config/awci/clouds/cloud-v1.json] [--write]

Prints the result as JSON. With --write, stores rh_critical and a `calibration` record (runs, steps,
cells, RMSE before/after, mean bias, date, git sha) in the profile and bumps its minor version.
Cubes must contain r, sp_hpa and tcc (any SP1 or SP1C cube does).
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from acf.awci.ops.calibration import calibrate_rhc
from acf.awci.ops.cloud_profile import DEFAULT_CLOUD_PROFILE_PATH, load_cloud_profile
from acf.awci.ops.ingest import parse_steps
from acf.awci.ops.store import CubeStore, _git_sha


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--domain", required=True)
    parser.add_argument("--runs", required=True, help="comma-separated YYYYMMDDHH")
    parser.add_argument("--steps", default="0-72/6")
    parser.add_argument("--data-dir", type=Path, default=None)
    parser.add_argument("--profile", type=Path, default=DEFAULT_CLOUD_PROFILE_PATH)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    store, wanted = CubeStore(args.data_dir), set(parse_steps(args.steps))
    r, sp, tcc, used = [], [], [], []
    levels: np.ndarray | None = None
    for run in args.runs.split(","):
        manifest = store.manifest(args.domain, run)
        ds = store.dataset(args.domain, run)
        levels = np.asarray(manifest["levels_hpa"], dtype=float)
        for si, step in enumerate(manifest["steps"]):
            if step in wanted and step not in manifest["missing_steps"]:
                r.append(ds["r"].isel(step=si).values)
                sp.append(ds["sp_hpa"].isel(step=si).values)
                tcc.append(ds["tcc"].isel(step=si).values)
                used.append(step)
    if levels is None or not r:
        raise SystemExit("no usable step in the requested runs")
    profile = load_cloud_profile(args.profile)
    result = calibrate_rhc(np.stack(r), np.stack(sp), levels, np.stack(tcc), profile)
    result |= {"runs": args.runs.split(","), "steps": sorted(set(used)), "domain": args.domain,
               "date": datetime.now(UTC).date().isoformat(), "acf_git_sha": _git_sha(),
               "rh_critical_before": dict(profile.rh_critical)}
    print(json.dumps(result, indent=2))
    if args.write:
        raw = json.loads(args.profile.read_text(encoding="utf-8"))
        major, minor, _patch = (int(x) for x in raw["version"].split("."))
        raw["version"] = f"{major}.{minor + 1}.0"
        raw["rh_critical"] = result["rh_critical"]
        raw["calibration"] = result
        args.profile.write_text(json.dumps(raw, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
