"""
acf-awci-obs: one ingestion pass of aeronautical observations (AWC METAR, TAF, international SIGMET).

    acf-awci-obs --domain north_africa [--hours 3] [--data-dir DIR]
    acf-awci-obs --domain north_africa --soundings [--hours 48]     # radiosondes (SP7) instead of AWC products

Run it every 10-30 minutes (cron/systemd, like acf-awci-ingest); `--hours 72` backfills the METAR of a
whole forecast run (the AWC keeps at least 7 days). Exit status 1 when the AWC could not be reached.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from pathlib import Path

from loguru import logger

from acf.awci.obs.source_awc import AwcClient, AwcError, UrllibAwcFetcher
from acf.awci.obs.sounding import (
    ATTRIBUTION,
    IGRA_STATIONS_URL,
    SoundingError,
    SoundingStation,
    UwyoClient,
    parse_igra_stations,
    stations_in,
)
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


SOUNDING_HOURS = (0, 12)
SOUNDING_DELAY = timedelta(hours=2)  # Wyoming publishes a sounding some time after the launch


def sounding_times(now: datetime, hours: int) -> list[datetime]:
    """Nominal 00/12 UTC soundings of the last `hours` hours, published by now (older first)."""
    t = now.replace(minute=0, second=0, microsecond=0)
    out = []
    while now - t <= timedelta(hours=hours):
        if t.hour in SOUNDING_HOURS and now - t >= SOUNDING_DELAY:
            out.append(t)
        t -= timedelta(hours=1)
    return sorted(out)


def ingest_soundings(client: UwyoClient, store: ObsStore, domain: Domain, hours: int, now: datetime,
                     fetch_station_list: Callable[[], str]) -> dict[str, object]:
    """Radiosondes of the domain's active IGRA stations over the last `hours` hours (station list cached a week)."""
    fetched = store.stations_fetched_at_of("sounding_stations.json")
    if fetched is None or now - fetched > STATION_MAX_AGE:
        listed = parse_igra_stations(fetch_station_list())
        if not listed:
            raise SoundingError("the IGRA station list is empty or unreadable")
        stations = stations_in(listed, domain, active_since=now.year)
        store.write_sounding_stations([s.as_dict() for s in stations], now)
    stations = [SoundingStation(**s) for s in store.sounding_stations()]  # type: ignore[arg-type]
    times = sounding_times(now, hours)
    added = store.add_soundings(client.soundings(stations, times))
    return {"soundings_added": added, "stations": len(stations), "times": [f"{t:%Y%m%d%H}" for t in times],
            "missing": len(client.missing), "errors": len(client.errors), "source": ATTRIBUTION}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="acf-awci-obs", description="Ingest AWC METAR, TAF and SIGMET")
    parser.add_argument("--domain", default="all")
    parser.add_argument("--hours", type=int, default=3, help="METAR history to fetch (1-168 h)")
    parser.add_argument("--domains-file", default=str(DEFAULT_DOMAINS_PATH))
    parser.add_argument("--data-dir", default=None)
    parser.add_argument("--retention-days", type=int, default=10)
    parser.add_argument("--soundings", action="store_true", help="ingest radiosondes (University of Wyoming) instead")
    args = parser.parse_args(argv)
    if not 1 <= args.hours <= 168:
        parser.error("--hours must be within 1-168")
    domains = load_domains(args.domains_file)
    chosen = list(domains.values()) if args.domain == "all" else [domains[args.domain]]
    root = Path(args.data_dir) if args.data_dir else data_root()
    status = 0
    if args.soundings:
        for domain in chosen:
            try:
                result = ingest_soundings(UwyoClient(), ObsStore(root, domain.name), domain, args.hours,
                                          datetime.now(UTC), lambda: UwyoClient._http_get(IGRA_STATIONS_URL))
                logger.info(f"AWCI soundings {domain.name}: {result}")
            except SoundingError as exc:
                logger.error(f"AWCI soundings {domain.name}: {exc}")
                status = 1
        return status
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
