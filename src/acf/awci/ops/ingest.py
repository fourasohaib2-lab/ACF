"""
acf-awci-ingest: download one ECMWF IFS run, compute AWCI layers, store cubes.

    acf-awci-ingest [--model ifs|gfs] [--run latest|YYYYMMDDHH] [--domain NAME|all] [--steps 0-72/3]
                    [--profile PATH] [--cloud-profile PATH] [--domains-file PATH] [--data-dir PATH]
                    [--keep N] [--force]

--model gfs ingests NOAA GFS 0.25° through the same pipeline (acf.awci.ops.source_gfs, spec SP6) into
<data>/gfs/; the default stays ECMWF IFS at the data root.

Exit code 0 when every domain is complete or partial, 1 when any failed.
A failed step never aborts the run; a run with no step at all is 'failed' and not stored.
Accumulated layers of a step are differenced against the previous *ingested* step only;
after a failed step they are NaN (accumulation_interval_h = null in the manifest).
"""

from __future__ import annotations

import argparse
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from loguru import logger

import numpy as np

from acf.awci.ops.cloud_profile import DEFAULT_CLOUD_PROFILE_PATH, CloudProfile, load_cloud_profile
from acf.awci.ops.decode import StepFields, decode_messages
from acf.awci.ops.domains import DEFAULT_DOMAINS_PATH, Domain, load_domains
from acf.awci.ops.engine import DEFAULT_OPERATIONAL_PROFILE_PATH, Profile, load_profile
from acf.awci.ops.pipeline import compute_step
from acf.awci.ops.source_ecmwf import (
    Fetcher,
    FetchError,
    MissingFieldsError,
    UrllibFetcher,
    fetch_step_messages,
    find_latest_run,
)
from acf.awci.ops.source_gfs import ATTRIBUTION as GFS_ATTRIBUTION
from acf.awci.ops.source_gfs import DIFFERENCES as GFS_DIFFERENCES
from acf.awci.ops.source_gfs import LICENSE as GFS_LICENSE
from acf.awci.ops.source_gfs import MODEL as GFS_MODEL
from acf.awci.ops.source_gfs import GfsRunState, decode_gfs, fetch_gfs_step, gfs_step_urls
from acf.awci.ops.store import CubeWriter, apply_retention, data_root, model_root
from acf.awci.terrain_elevation import interpolate_real_terrain_elevation


def parse_steps(spec: str) -> list[int]:
    if "-" in spec:
        span, _, stride = spec.partition("/")
        start, end = (int(x) for x in span.split("-"))
        step = int(stride or 3)
        if step <= 0 or start > end:
            raise ValueError(f"invalid steps spec {spec!r}")
        return list(range(start, end + 1, step))
    return [int(x) for x in spec.split(",")]


def _consistency(step: int, bias: np.ndarray, cloud_profile: CloudProfile) -> dict[str, Any]:
    """Domain mean/std of (diagnosed - IFS tcc); |mean| above the profile threshold flags the step."""
    finite = bias[np.isfinite(bias)]
    if finite.size == 0:
        return {"step": step, "bias_mean": None, "bias_std": None, "status": "degraded"}
    mean = float(finite.mean())
    return {"step": step, "bias_mean": round(mean, 4), "bias_std": round(float(finite.std()), 4),
            "status": "degraded" if abs(mean) > cloud_profile.bias_degraded_threshold else "ok"}


def ingest_run(
    run: datetime, domains: list[Domain], profile: Profile, fetcher: Fetcher, root: Path,
    steps: list[int], keep: int | None = 8, force: bool = False, cloud_profile: CloudProfile | None = None,
    model: str = "ifs",
) -> dict[str, dict[str, Any]]:
    """Ingest one run of `model` ("ifs" or "gfs") into `root` (the model's own directory, see store.model_root)."""
    if model not in ("ifs", "gfs"):
        raise ValueError(f"unknown model {model!r}")
    gfs_state = GfsRunState()
    started = time.monotonic()
    cloud_profile = cloud_profile or load_cloud_profile(DEFAULT_CLOUD_PROFILE_PATH)
    writers: dict[str, CubeWriter] = {}
    elevations: dict[str, Any] = {}
    missing: list[int] = []
    intervals: list[int | None] = []
    consistency: dict[str, list[dict[str, Any]]] = {d.name: [] for d in domains}
    previous: dict[str, StepFields] = {}
    prev_step: int | None = None
    for index, step in enumerate(steps):
        try:
            if model == "gfs":
                per_domain = decode_gfs(fetch_gfs_step(fetcher, run, step), domains, step, gfs_state)
            else:
                per_domain = decode_messages(fetch_step_messages(fetcher, run, step), domains)
        except (FetchError, MissingFieldsError, ValueError) as exc:
            logger.warning("AWCI ingest {} step {}h skipped: {}", run, step, exc)
            missing.append(step)
            intervals.append(None)
            previous.clear()
            prev_step = None
            continue
        interval = step - prev_step if prev_step is not None else None
        intervals.append(interval)
        for domain in domains:
            fields = per_domain[domain.name]
            if domain.name not in writers:
                elevations[domain.name] = interpolate_real_terrain_elevation(fields.lats, fields.lons)
                writers[domain.name] = CubeWriter(root, domain, run, fields.lats, fields.lons, fields.levels_hpa,
                                                  steps, profile)
            layers = compute_step(fields, elevations[domain.name], profile, cloud_profile,
                                  previous.get(domain.name), interval)
            writers[domain.name].write_step(index, layers, elevations[domain.name])
            consistency[domain.name].append(_consistency(step, layers["cloud_cover_bias"], cloud_profile))
            previous[domain.name] = fields
        prev_step = step
        logger.info("AWCI ingest {} step {}h done", run, step)
    manifests: dict[str, dict[str, Any]] = {}
    status = "failed" if len(missing) == len(steps) else ("partial" if missing else "complete")
    for domain in domains:
        writer = writers.get(domain.name)
        if writer is None:
            manifests[domain.name] = {"status": "failed", "domain": domain.name, "missing_steps": missing}
            continue
        checks = consistency[domain.name]
        extra = {
            "duration_s": round(time.monotonic() - started, 1),
            "cloud_profile": cloud_profile.name, "cloud_profile_version": cloud_profile.version,
            "accumulation_interval_h": intervals, "cloud_consistency": checks,
            "cloud_status": "degraded" if any(c["status"] == "degraded" for c in checks) else "ok",
            "model_id": model,
        }
        if model == "gfs":
            extra |= {"model": GFS_MODEL, "license": GFS_LICENSE, "attribution": GFS_ATTRIBUTION,
                      "definition_differences": GFS_DIFFERENCES}
        manifests[domain.name] = writer.finalize(status, missing, extra, force=force)
        apply_retention(root, domain.name, keep)
    return manifests


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="acf-awci-ingest", description=__doc__.splitlines()[1])
    parser.add_argument("--model", choices=("ifs", "gfs"), default="ifs")
    parser.add_argument("--run", default="latest")
    parser.add_argument("--domain", default="all")
    parser.add_argument("--steps", default="0-72/3")
    parser.add_argument("--profile", default=str(DEFAULT_OPERATIONAL_PROFILE_PATH))
    parser.add_argument("--cloud-profile", default=str(DEFAULT_CLOUD_PROFILE_PATH))
    parser.add_argument("--domains-file", default=str(DEFAULT_DOMAINS_PATH))
    parser.add_argument("--data-dir", default=None)
    parser.add_argument("--keep", type=int, default=8)
    parser.add_argument("--force", action="store_true", help="replace a complete run even with a partial rerun")
    args = parser.parse_args(argv)

    steps = parse_steps(args.steps)
    all_domains = load_domains(args.domains_file)
    domains = list(all_domains.values()) if args.domain == "all" else [all_domains[args.domain]]
    fetcher = UrllibFetcher()
    urls = gfs_step_urls if args.model == "gfs" else None
    run = ((find_latest_run(fetcher, datetime.now(UTC), steps[-1], urls=urls) if urls else
            find_latest_run(fetcher, datetime.now(UTC), steps[-1])) if args.run == "latest"
           else datetime.strptime(args.run, "%Y%m%d%H").replace(tzinfo=UTC))
    root = model_root(Path(args.data_dir) if args.data_dir else data_root(), args.model)
    manifests = ingest_run(run, domains, load_profile(args.profile), fetcher, root, steps, args.keep, args.force,
                           load_cloud_profile(args.cloud_profile), model=args.model)
    for name, manifest in manifests.items():
        logger.info("AWCI ingest {} {}: {}", run, name, manifest["status"])
    return 1 if any(m["status"] == "failed" for m in manifests.values()) else 0


if __name__ == "__main__":
    raise SystemExit(main())
