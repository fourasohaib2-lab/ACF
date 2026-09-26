"""
acf-awci-obs: one ingestion pass of aeronautical observations (AWC METAR, TAF, international SIGMET).

    acf-awci-obs --domain north_africa [--hours 3] [--data-dir DIR]

Run it every 10-30 minutes (cron/systemd, like acf-awci-ingest); `--hours 72` backfills the METAR of a
whole forecast run (the AWC keeps at least 7 days). Exit status 1 when the AWC could not be reached.
"""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

from loguru import logger

from acf.awci.obs.source_awc import AwcClient, AwcError, UrllibAwcFetcher
from acf.awci.obs.store import ObsStore
from acf.awci.ops.domains import DEFAULT_DOMAINS_PATH, Domain, load_domains
from acf.awci.ops.store import data_root

STATION_MAX_AGE = timedelta(days=7)


def ingest_domain(client: AwcClient, store: ObsStore, domain: Domain, hours: int, now: datetime,
                  retention_days: int) -> dict[str, object]:
    fetched = store.stations_fetched_at()
    if fetched is None or now - fetched > STATION_MAX_AGE:
        store.write_stations([s.as_dict() for s in client.stations(domain)], now)
    stations = store.stations()
    ids = [s["icao"] for s in stations]
    added = store.add_metars(client.metars(ids, hours))
    tafs = client.tafs([s["icao"] for s in stations if s.get("taf")])
    store.write_tafs(tafs)
    sigmets_added = store.add_sigmets(client.isigmets(domain))
    removed = store.apply_retention(retention_days, now)
    status: dict[str, object] = {
        "ingested_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "stations": len(stations), "metars_added": added,
        "tafs": len(tafs), "sigmets_added": sigmets_added, "rejected": client.rejected, "removed": removed,
        "source": "NOAA/NWS Aviation Weather Center Data API", "hours": hours,
    }
    store.write_status(status)
    return status


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="acf-awci-obs", description="Ingest AWC METAR, TAF and SIGMET")
    parser.add_argument("--domain", default="all")
    parser.add_argument("--hours", type=int, default=3, help="METAR history to fetch (1-168 h)")
    parser.add_argument("--domains-file", default=str(DEFAULT_DOMAINS_PATH))
    parser.add_argument("--data-dir", default=None)
    parser.add_argument("--retention-days", type=int, default=10)
    args = parser.parse_args(argv)
    if not 1 <= args.hours <= 168:
        parser.error("--hours must be within 1-168")
    domains = load_domains(args.domains_file)
    chosen = list(domains.values()) if args.domain == "all" else [domains[args.domain]]
    root = Path(args.data_dir) if args.data_dir else data_root()
    status = 0
    for domain in chosen:
        client = AwcClient(UrllibAwcFetcher())
        try:
            result = ingest_domain(client, ObsStore(root, domain.name), domain, args.hours, datetime.now(UTC),
                                   args.retention_days)
            logger.info(f"AWCI obs {domain.name}: {result}")
        except AwcError as exc:
            logger.error(f"AWCI obs {domain.name}: {exc}")
            status = 1
    return status


if __name__ == "__main__":
    sys.exit(main())
