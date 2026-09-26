"""
End-to-end test server for web/awci (Playwright `webServer`).

Ingests the real cropped IFS fixtures into a data directory, then serves the API and the built
front with an offline EUMETView relay: capabilities come from the real excerpt in tests/data/wms,
tiles are transparent PNGs, `msg_fes:rgb_ash` always fails so the "EUMETView unavailable" state can
be exercised, and `mtg_fd:rgb_dust` hangs until the relay's upstream timeout, like a slow EUMETView,
so the forecast's independence from the relay can be measured. No network access.

    .venv/bin/python tools/awci/e2e_server.py --port 8099 [--data-dir DIR] [--web-dist DIR]

Domains: `fixture` (35-37N / 2-4E, complete run, steps 0 and 3) and `fixture_wet`
(15-17N / 20-18W, partial run: step 6 requested but absent from the fixture).

NOAA GFS (SP6): the `fixture` domain also gets the real cropped GFS run of the same analysis time (+0, +3, +6 h),
so the model selector and the IFS-GFS comparison are exercised; `fixture_wet` has no GFS run.

IFS ENS: the `fixture` domain also gets the real 4-member ENS fixture of the same run (+0 and +6 h).

Aeronautical observations: the `fixture` domain gets the real recorded AWC data of Algiers (DAAG): its
METAR of 2026-09-24 21Z .. 2026-09-25 14Z and its TAF (tests/data/awc). `fixture_wet` has none, so the
"no observation ingested" state is exercised too.
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
import tempfile
import time
import zlib
from datetime import UTC, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))  # tests.awci_ops_support

from acf.awci.ops.engine import DEFAULT_OPERATIONAL_PROFILE_PATH, load_profile  # noqa: E402
from acf.awci.ops.ingest import ingest_run  # noqa: E402
from acf.web.awci_app import create_awci_app  # noqa: E402
from acf.awci.obs.source_awc import AwcClient  # noqa: E402
from acf.awci.obs.store import ObsStore  # noqa: E402
from acf.awci.ops.ens_ingest import ingest_ens_run  # noqa: E402
from acf.web.awci_wms import WmsRelay  # noqa: E402
from tests.awci_ops_support import (  # noqa: E402
    DOMAIN, ENS_FIXTURE, WET_DOMAIN, WET_FIXTURE, FixtureFetcher, GfsFixtureFetcher,
)

CAPABILITIES = (REPO / "tests" / "data" / "wms" / "eumetview_capabilities_excerpt.xml").read_bytes()
FAILING_LAYER = "msg_fes:rgb_ash"
SLOW_LAYER = "mtg_fd:rgb_dust"
RUN = datetime(2026, 9, 25, 0, tzinfo=UTC)
AWC = REPO / "tests" / "data" / "awc"
DAAG = {"icao": "DAAG", "name": "Algiers Intl", "lat": 36.691, "lon": 3.215, "elev_m": 18.0, "metar": True, "taf": True}


def prepare_observations(data_dir: Path) -> None:
    store = ObsStore(data_dir, DOMAIN.name)
    store.write_stations([DAAG], datetime(2026, 9, 26, tzinfo=UTC))
    store.add_metars([r for r in map(AwcClient._metar, json.loads((AWC / "metar_daag_20260925.json").read_text())) if r])
    store.write_tafs([r for r in map(AwcClient._taf, json.loads((AWC / "taf_sample_20260926T08.json").read_text()))
                      if r and r["icao"] == "DAAG"])
    store.write_status({"ingested_at": "2026-09-26T08:52:54Z", "stations": 1,
                        "source": "recorded AWC responses (tests/data/awc)"})


def transparent_png(size: int = 256) -> bytes:
    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    rows = b"".join(b"\x00" + b"\x00\x00\x00\x00" * size for _ in range(size))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b""))


class OfflineWmsFetcher:
    def __init__(self) -> None:
        self.tile = transparent_png()

    def get(self, url: str, timeout: float) -> tuple[str, bytes]:
        if "GetCapabilities" in url:
            return "text/xml", CAPABILITIES
        if FAILING_LAYER.replace(":", "%3A") in url:
            raise OSError("offline test relay: simulated EUMETView failure")
        if SLOW_LAYER.replace(":", "%3A") in url:
            time.sleep(timeout)
            raise TimeoutError("offline test relay: simulated slow EUMETView")
        return "image/png", self.tile


def prepare(data_dir: Path) -> Path:
    profile = load_profile(DEFAULT_OPERATIONAL_PROFILE_PATH)
    ingest_run(RUN, [DOMAIN], profile, FixtureFetcher(), data_dir, [0, 3])
    ingest_run(RUN, [WET_DOMAIN], profile, FixtureFetcher(root=WET_FIXTURE), data_dir, [0, 3, 6])
    prepare_observations(data_dir)
    # IFS ENS (real 4-member fixture, same run): +0 and +6 h, so +3 h exercises "not computed by the ensemble"
    ingest_ens_run(RUN, DOMAIN, FixtureFetcher(root=ENS_FIXTURE), data_dir, steps=[0, 6], members=[1, 2, 3, 4])
    # SP6: the real cropped GFS run of the same analysis time (+0, +3, +6 h) for the fixture domain
    ingest_run(RUN, [DOMAIN], profile, GfsFixtureFetcher(), data_dir / "gfs", [0, 3, 6], model="gfs")
    domains = data_dir / "domains.json"
    domains.write_text(json.dumps({"domains": [
        {"name": d.name, "label": d.label, "south": d.south, "north": d.north, "west": d.west, "east": d.east,
         "default": d.name == DOMAIN.name} for d in (DOMAIN, WET_DOMAIN)]}))
    return domains


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="AWCI Web end-to-end test server (offline)")
    parser.add_argument("--port", type=int, default=8099)
    parser.add_argument("--data-dir", type=Path, default=None)
    parser.add_argument("--web-dist", type=Path, default=REPO / "web" / "awci" / "dist")
    args = parser.parse_args(argv)
    data_dir = args.data_dir or Path(tempfile.mkdtemp(prefix="awci-e2e-"))
    domains = prepare(data_dir)
    app = create_awci_app(data_dir=data_dir, domains_file=domains, web_dist=args.web_dist)
    app.state.awci_wms = WmsRelay(OfflineWmsFetcher(), data_dir / ".wms-cache")

    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
