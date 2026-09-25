"""
End-to-end test server for web/awci (Playwright `webServer`).

Ingests the real cropped IFS fixtures into a data directory, then serves the API and the built
front with an offline EUMETView relay: capabilities come from the real excerpt in tests/data/wms,
tiles are transparent PNGs, and `msg_fes:rgb_ash` always fails so the "EUMETView unavailable"
state can be exercised. No network access.

    .venv/bin/python tools/awci/e2e_server.py --port 8099 [--data-dir DIR] [--web-dist DIR]

Domains: `fixture` (35-37N / 2-4E, complete run, steps 0 and 3) and `fixture_wet`
(15-17N / 20-18W, partial run: step 6 requested but absent from the fixture).
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
import tempfile
import zlib
from datetime import UTC, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))  # tests.awci_ops_support

from acf.awci.ops.engine import DEFAULT_OPERATIONAL_PROFILE_PATH, load_profile  # noqa: E402
from acf.awci.ops.ingest import ingest_run  # noqa: E402
from acf.web.awci_app import create_awci_app  # noqa: E402
from acf.web.awci_wms import WmsRelay  # noqa: E402
from tests.awci_ops_support import DOMAIN, WET_DOMAIN, WET_FIXTURE, FixtureFetcher  # noqa: E402

CAPABILITIES = (REPO / "tests" / "data" / "wms" / "eumetview_capabilities_excerpt.xml").read_bytes()
FAILING_LAYER = "msg_fes:rgb_ash"
RUN = datetime(2026, 9, 25, 0, tzinfo=UTC)


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
        return "image/png", self.tile


def prepare(data_dir: Path) -> Path:
    profile = load_profile(DEFAULT_OPERATIONAL_PROFILE_PATH)
    ingest_run(RUN, [DOMAIN], profile, FixtureFetcher(), data_dir, [0, 3])
    ingest_run(RUN, [WET_DOMAIN], profile, FixtureFetcher(root=WET_FIXTURE), data_dir, [0, 3, 6])
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
