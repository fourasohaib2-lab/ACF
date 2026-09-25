"""EUMETView WMS relay: allow-list, validation, latest time, disk cache, upstream failures."""

import struct
import zlib
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from acf.web.awci_app import create_awci_app
from acf.web.awci_wms import WMS_LAYERS, WmsRelay, capabilities_time_dimensions, parse_time_dimension

CAPS = (Path(__file__).parent / "data" / "wms" / "eumetview_capabilities_excerpt.xml").read_bytes()


def _png() -> bytes:
    raw = b"\x00\x00\x00\x00\x00"
    def chunk(t: bytes, d: bytes) -> bytes:
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


class FakeFetcher:
    def __init__(self, fail: bool = False, xml_error: bool = False) -> None:
        self.calls: list[str] = []
        self.fail, self.xml_error = fail, xml_error

    def get(self, url: str, timeout: float) -> tuple[str, bytes]:
        self.calls.append(url)
        if self.fail:
            raise OSError("upstream down")
        if "GetCapabilities" in url:
            return "text/xml", CAPS
        return ("text/xml", b"<ServiceExceptionReport/>") if self.xml_error else ("image/png", _png())


def _client(tmp_path: Path, fetcher: FakeFetcher) -> TestClient:
    app = create_awci_app(data_dir=tmp_path)
    app.state.awci_wms = WmsRelay(fetcher, tmp_path / "wms-cache")
    return TestClient(app)


BBOX = "0,4000000,500000,4500000"


def test_time_dimension_interval_and_list() -> None:
    times = parse_time_dimension("2026-09-25T18:00:00.000Z/2026-09-25T18:30:00.000Z/PT10M", 3)
    assert times == [datetime(2026, 9, 25, 18, m, tzinfo=UTC) for m in (10, 20, 30)]
    assert parse_time_dimension("2026-09-25T18:00:00Z,2026-09-25T18:15:00Z", 5)[-1].minute == 15


def test_real_capabilities_excerpt_covers_the_allow_list() -> None:
    dims = capabilities_time_dimensions(CAPS)
    assert set(WMS_LAYERS) <= set(dims)


def test_tile_uses_latest_time_and_is_cached(tmp_path: Path) -> None:
    f = FakeFetcher()
    c = _client(tmp_path, f)
    r = c.get("/api/v1/awci/wms", params={"layer": "mtg_fd:ir105_hrfi", "bbox": BBOX, "width": 256, "height": 256})
    assert r.status_code == 200 and r.headers["content-type"] == "image/png"
    assert r.headers["x-awci-observed-at"].endswith("Z") and "EUMETSAT" in r.headers["x-awci-attribution"]
    n = len(f.calls)
    c.get("/api/v1/awci/wms", params={"layer": "mtg_fd:ir105_hrfi", "bbox": BBOX, "width": 256, "height": 256,
                                      "time": r.headers["x-awci-observed-at"]})
    assert len(f.calls) == n  # same explicit time -> disk cache


@pytest.mark.parametrize("params,status", [
    ({"layer": "evil:layer"}, 400),
    ({"bbox": "0,0,1"}, 400),
    ({"bbox": "0,0,99999999,1"}, 400),
    ({"width": 4096}, 422),
    ({"time": "yesterday"}, 400),
])
def test_invalid_requests_rejected(tmp_path: Path, params: dict, status: int) -> None:
    base = {"layer": "mtg_fd:ir105_hrfi", "bbox": BBOX, "width": 256, "height": 256}
    assert _client(tmp_path, FakeFetcher()).get("/api/v1/awci/wms", params=base | params).status_code == status


@pytest.mark.parametrize("fetcher", [FakeFetcher(fail=True), FakeFetcher(xml_error=True)])
def test_upstream_failure_is_502(tmp_path: Path, fetcher: FakeFetcher) -> None:
    r = _client(tmp_path, fetcher).get("/api/v1/awci/wms", params={"layer": "mtg_fd:ir105_hrfi", "bbox": BBOX,
                                                                  "width": 256, "height": 256})
    assert r.status_code == 502


def test_times_route(tmp_path: Path) -> None:
    body = _client(tmp_path, FakeFetcher()).get("/api/v1/awci/wms/times",
                                                params={"layer": "mtg_fd:li_afa", "count": 6}).json()
    assert len(body["times"]) == 6 and body["times"] == sorted(body["times"])


@pytest.mark.skipif(not __import__("os").environ.get("ACF_AWCI_NETWORK_TESTS"), reason="real network: opt-in")
def test_real_eumetview_latest_ir_tile(tmp_path: Path) -> None:
    from acf.web.awci_wms import UrllibWmsFetcher

    app = create_awci_app(data_dir=tmp_path)
    app.state.awci_wms = WmsRelay(UrllibWmsFetcher(), tmp_path / "cache")
    c = TestClient(app)
    latest = c.get("/api/v1/awci/wms/times", params={"layer": "mtg_fd:ir105_hrfi"}).json()["times"][-1]
    age = datetime.now(UTC) - datetime.fromisoformat(latest.replace("Z", "+00:00"))
    assert age.total_seconds() < 2 * 3600
    r = c.get("/api/v1/awci/wms", params={"layer": "mtg_fd:ir105_hrfi", "bbox": "0,4000000,500000,4500000",
                                          "width": 256, "height": 256})
    assert r.status_code == 200 and r.content[:8] == b"\x89PNG\r\n\x1a\n" and len(r.content) > 1000
