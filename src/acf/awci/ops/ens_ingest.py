"""
acf-awci-ens: IFS ENS probabilities and spread for one run (spec SP5).

    acf-awci-ens --run latest --domain north_africa [--steps 0-48/6] [--members 1-50] [--connections 16]

Per step the ENS index is read once; each member is then streamed: its messages downloaded (HTTP ranges,
`connections` in parallel, the next members preloaded), decoded and cropped, passed through the unchanged
deterministic pipeline (compute_step, same relief and profiles), counted, and freed. eccodes is not
thread-safe: decoding stays sequential. A member that fails is excluded and recorded, never replaced; a step
without any member is missing.
"""

from __future__ import annotations

import argparse
import sys
import time
from collections import deque
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from loguru import logger

from acf.awci.ops.cloud_profile import DEFAULT_CLOUD_PROFILE_PATH, CloudProfile, load_cloud_profile
from acf.awci.ops.decode import decode_messages
from acf.awci.ops.domains import DEFAULT_DOMAINS_PATH, Domain, load_domains
from acf.awci.ops.engine import DEFAULT_OPERATIONAL_PROFILE_PATH, Profile, load_profile
from acf.awci.ops.ens_store import EnsWriter, apply_ens_retention
from acf.awci.ops.ensemble import EnsembleAccumulator, class_lower_bound
from acf.awci.ops.ingest import parse_steps
from acf.awci.ops.pipeline import compute_step
from acf.awci.ops.source_ecmwf import (
    Fetcher, FetchError, IndexEntry, MissingFieldsError, UrllibFetcher, ens_step_urls, find_latest_run, parse_index,
    select_entries,
)
from acf.awci.ops.store import data_root
from acf.awci.terrain_elevation import interpolate_real_terrain_elevation

PREFETCH_MEMBERS = 2


def _submit(pool: ThreadPoolExecutor, fetcher: Fetcher, grib_url: str, index: list[IndexEntry],
            member: int) -> list[Future[bytes]] | Exception:
    try:
        entries = select_entries(index, member=member)
    except MissingFieldsError as exc:
        return exc
    return [pool.submit(fetcher.get_range, grib_url, e.offset, e.length) for e in entries]


def ingest_ens_run(run: datetime, domain: Domain, fetcher: Fetcher, root: Path, steps: list[int], members: list[int],
                   profile: Profile | None = None, cloud_profile: CloudProfile | None = None,
                   connections: int = 16, keep: int | None = 4) -> dict[str, Any]:
    started = time.monotonic()
    profile = profile or load_profile(DEFAULT_OPERATIONAL_PROFILE_PATH)
    cloud_profile = cloud_profile or load_cloud_profile(DEFAULT_CLOUD_PROFILE_PATH)
    awci_high = class_lower_bound(profile, "High")
    writer: EnsWriter | None = None
    elevation = None
    missing: list[int] = []
    used: dict[str, int] = {}
    failed: dict[str, list[int]] = {}
    with ThreadPoolExecutor(max_workers=connections) as pool:
        for index_pos, step in enumerate(steps):
            grib_url, index_url = ens_step_urls(run, step)
            try:
                index = parse_index(fetcher.get_text(index_url))
            except FetchError as exc:
                logger.warning("AWCI ENS {} step {}h skipped: {}", run, step, exc)
                missing.append(step)
                continue
            acc: EnsembleAccumulator | None = None
            failed[str(step)] = []
            queue: deque[tuple[int, list[Future[bytes]] | Exception]] = deque()
            pending = list(members)
            while pending or queue:
                while pending and len(queue) <= PREFETCH_MEMBERS:
                    member = pending.pop(0)
                    queue.append((member, _submit(pool, fetcher, grib_url, index, member)))
                member, futures = queue.popleft()
                try:
                    if isinstance(futures, Exception):
                        raise futures
                    fields = decode_messages([f.result() for f in futures], [domain])[domain.name]
                    if elevation is None:
                        elevation = interpolate_real_terrain_elevation(fields.lats, fields.lons)
                    layers = compute_step(fields, elevation, profile, cloud_profile)
                except (FetchError, MissingFieldsError, ValueError) as exc:
                    logger.warning("AWCI ENS {} step {}h member {} excluded: {}", run, step, member, exc)
                    failed[str(step)].append(member)
                    continue
                if writer is None:
                    writer = EnsWriter(root, domain, run, fields.lats, fields.lons, fields.levels_hpa, steps)
                if acc is None:
                    acc = EnsembleAccumulator(layers["awci"].shape, layers["ceiling_m"].shape, awci_high)
                acc.add(layers)
            if acc is None or writer is None:
                missing.append(step)
                continue
            used[str(step)] = acc.members
            writer.write_step(index_pos, acc.result())
            logger.info("AWCI ENS {} step {}h: {} members", run, step, acc.members)
    if writer is None:
        raise FetchError(f"no ENS member could be processed for {run:%Y%m%d%H}")
    manifest = writer.finalize(missing, {
        "members_requested": members, "members_used": used,
        "failed_members": {k: v for k, v in failed.items() if v},
        "profile": profile.name, "profile_version": profile.version, "awci_high_lower_bound": awci_high,
        "cloud_profile": cloud_profile.name, "cloud_profile_version": cloud_profile.version,
        "duration_s": round(time.monotonic() - started, 1),
    })
    apply_ens_retention(root, domain.name, keep)
    return manifest


def parse_members(spec: str) -> list[int]:
    members = parse_steps(spec if "/" in spec or "," in spec or "-" not in spec else f"{spec}/1")
    if not members or min(members) < 1 or max(members) > 50:
        raise ValueError(f"members must lie within 1-50, got {spec!r}")
    return members


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="acf-awci-ens", description="IFS ENS probabilities for AWCI Web")
    parser.add_argument("--run", default="latest")
    parser.add_argument("--domain", required=True)
    parser.add_argument("--steps", default="0-48/6")
    parser.add_argument("--members", default="1-50")
    parser.add_argument("--connections", type=int, default=16)
    parser.add_argument("--domains-file", default=str(DEFAULT_DOMAINS_PATH))
    parser.add_argument("--data-dir", default=None)
    parser.add_argument("--keep", type=int, default=4)
    args = parser.parse_args(argv)
    if not 1 <= args.connections <= 32:
        parser.error("--connections must lie within 1-32 (be fair to data.ecmwf.int)")
    fetcher = UrllibFetcher()
    steps, members = parse_steps(args.steps), parse_members(args.members)
    run = (find_latest_run(fetcher, datetime.now(UTC), steps[-1], urls=ens_step_urls) if args.run == "latest"
           else datetime.strptime(args.run, "%Y%m%d%H").replace(tzinfo=UTC))
    domain = load_domains(args.domains_file)[args.domain]
    root = Path(args.data_dir) if args.data_dir else data_root()
    try:
        manifest = ingest_ens_run(run, domain, fetcher, root, steps, members, connections=args.connections, keep=args.keep)
    except FetchError as exc:
        logger.error("AWCI ENS {}: {}", run, exc)
        return 1
    logger.info("AWCI ENS {} {}: {} in {} s", run, domain.name, manifest["status"], manifest["duration_s"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
