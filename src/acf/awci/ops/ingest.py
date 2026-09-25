"""
acf-awci-ingest: download one ECMWF IFS run, compute AWCI layers, store cubes.

    acf-awci-ingest [--run latest|YYYYMMDDHH] [--domain NAME|all] [--steps 0-72/3]
                    [--profile PATH] [--domains-file PATH] [--data-dir PATH] [--keep N]

Exit code 0 when every domain is complete or partial, 1 when any failed.
A failed step never aborts the run; a run with no step at all is 'failed' and not stored.
"""

from __future__ import annotations

import argparse
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from loguru import logger

from acf.awci.ops.decode import decode_messages
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
from acf.awci.ops.store import CubeWriter, apply_retention, data_root
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


def ingest_run(
    run: datetime, domains: list[Domain], profile: Profile, fetcher: Fetcher, root: Path,
    steps: list[int], keep: int = 8,
) -> dict[str, dict[str, Any]]:
    started = time.monotonic()
    writers: dict[str, CubeWriter] = {}
    elevations: dict[str, Any] = {}
    missing: list[int] = []
    for index, step in enumerate(steps):
        try:
            per_domain = decode_messages(fetch_step_messages(fetcher, run, step), domains)
        except (FetchError, MissingFieldsError, ValueError) as exc:
            logger.warning("AWCI ingest {} step {}h skipped: {}", run, step, exc)
            missing.append(step)
            continue
        for domain in domains:
            fields = per_domain[domain.name]
            if domain.name not in writers:
                elevations[domain.name] = interpolate_real_terrain_elevation(fields.lats, fields.lons)
                writers[domain.name] = CubeWriter(root, domain, run, fields.lats, fields.lons, fields.levels_hpa,
                                                  steps, profile)
            writers[domain.name].write_step(index, compute_step(fields, elevations[domain.name], profile),
                                            elevations[domain.name])
        logger.info("AWCI ingest {} step {}h done", run, step)
    manifests: dict[str, dict[str, Any]] = {}
    status = "failed" if len(missing) == len(steps) else ("partial" if missing else "complete")
    for domain in domains:
        writer = writers.get(domain.name)
        if writer is None:
            manifests[domain.name] = {"status": "failed", "domain": domain.name, "missing_steps": missing}
            continue
        manifests[domain.name] = writer.finalize(status, missing, {"duration_s": round(time.monotonic() - started, 1)})
        apply_retention(root, domain.name, keep)
    return manifests


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="acf-awci-ingest", description=__doc__.splitlines()[1])
    parser.add_argument("--run", default="latest")
    parser.add_argument("--domain", default="all")
    parser.add_argument("--steps", default="0-72/3")
    parser.add_argument("--profile", default=str(DEFAULT_OPERATIONAL_PROFILE_PATH))
    parser.add_argument("--domains-file", default=str(DEFAULT_DOMAINS_PATH))
    parser.add_argument("--data-dir", default=None)
    parser.add_argument("--keep", type=int, default=8)
    args = parser.parse_args(argv)

    steps = parse_steps(args.steps)
    all_domains = load_domains(args.domains_file)
    domains = list(all_domains.values()) if args.domain == "all" else [all_domains[args.domain]]
    fetcher = UrllibFetcher()
    run = (find_latest_run(fetcher, datetime.now(UTC), steps[-1]) if args.run == "latest"
           else datetime.strptime(args.run, "%Y%m%d%H").replace(tzinfo=UTC))
    root = Path(args.data_dir) if args.data_dir else data_root()
    manifests = ingest_run(run, domains, load_profile(args.profile), fetcher, root, steps, args.keep)
    for name, manifest in manifests.items():
        logger.info("AWCI ingest {} {}: {}", run, name, manifest["status"])
    return 1 if any(m["status"] == "failed" for m in manifests.values()) else 0


if __name__ == "__main__":
    raise SystemExit(main())
