"""EUMETView WMS relay: allow-list, validation, latest time, disk cache, upstream failures."""

import os
import struct
import threading
import time
import zlib
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from acf.web.awci_app import create_awci_app
from acf.web.awci_wms import (
    WMS_LAYERS,
    WmsRelay,
    WmsUpstreamError,
    capabilities_time_dimensions,
    parse_time_dimension,
    tile_bbox,
    time_in_dimension,
)

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


BBOX = ",".join(f"{v:.6f}" for v in tile_bbox(6, 32, 25))  # a real XYZ tile, as MapLibre requests it


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


def _tile(c: TestClient, **extra: object):
    return c.get("/api/v1/awci/wms", params={"layer": "mtg_fd:ir105_hrfi", "bbox": BBOX, "width": 256,
                                             "height": 256, **extra})


def test_latest_time_across_several_intervals() -> None:
    dim = "2026-09-20T00:00:00Z/2026-09-24T00:00:00Z/PT1H,2026-09-25T00:00:00Z/2026-09-26T00:00:00Z/PT1H"
    assert parse_time_dimension(dim, 1) == [datetime(2026, 9, 26, tzinfo=UTC)]
    assert parse_time_dimension(dim, 30)[0] == datetime(2026, 9, 23, 20, tzinfo=UTC)  # 25 + 5 instants


def test_day_period_and_bad_period() -> None:
    assert parse_time_dimension("2026-09-20T00:00:00Z/2026-09-22T00:00:00Z/P1D", 5)[-1].day == 22
    with pytest.raises(ValueError):
        parse_time_dimension("2026-09-20T00:00:00Z/2026-09-22T00:00:00Z/P1W", 5)


def test_unparsable_upstream_dimension_is_502(tmp_path: Path) -> None:
    relay = WmsRelay(FakeFetcher(), tmp_path)
    relay._caps = (relay.clock(), {"mtg_fd:li_afa": "2026-09-20T00:00:00Z/2026-09-22T00:00:00Z/P1W"})
    with pytest.raises(WmsUpstreamError):
        relay.times("mtg_fd:li_afa", 1)


def test_time_membership() -> None:
    dim = "2026-09-25T18:00:00Z/2026-09-25T18:30:00Z/PT10M,2026-09-26T00:00:00Z"
    ok = [datetime(2026, 9, 25, 18, 20, tzinfo=UTC), datetime(2026, 9, 26, tzinfo=UTC)]
    ko = [datetime(2026, 9, 25, 18, 25, tzinfo=UTC), datetime(2026, 9, 25, 18, 40, tzinfo=UTC)]
    assert all(time_in_dimension(dim, t) for t in ok) and not any(time_in_dimension(dim, t) for t in ko)


def test_time_not_offered_upstream_is_rejected_without_getmap(tmp_path: Path) -> None:
    f = FakeFetcher()
    r = _tile(_client(tmp_path, f), time="2031-01-01T00:00:00Z")
    assert r.status_code == 400
    assert not [u for u in f.calls if "GetMap" in u]


def test_bbox_off_the_tile_grid_is_rejected(tmp_path: Path) -> None:
    r = _client(tmp_path, FakeFetcher()).get("/api/v1/awci/wms", params={
        "layer": "mtg_fd:ir105_hrfi", "bbox": "0,4000000,500000,4500000", "width": 256, "height": 256})
    assert r.status_code == 400


def test_tile_bbox_matches_web_mercator_grid() -> None:
    assert tile_bbox(0, 0, 0) == pytest.approx((-20037508.342789244, -20037508.342789244,
                                                 20037508.342789244, 20037508.342789244))


class SlowFetcher(FakeFetcher):
    def __init__(self) -> None:
        super().__init__()
        self.release = threading.Event()

    def get(self, url: str, timeout: float) -> tuple[str, bytes]:
        if "GetMap" in url:
            self.release.wait(timeout)
        return super().get(url, timeout)


def test_default_upstream_timeout_is_short(tmp_path: Path) -> None:
    assert WmsRelay(FakeFetcher(), tmp_path).timeout_s <= 5.0


def test_busy_relay_fails_fast_instead_of_queueing(tmp_path: Path) -> None:
    f = SlowFetcher()
    relay = WmsRelay(f, tmp_path, max_concurrent=1, queue_wait_s=0.05)
    bbox = tile_bbox(6, 32, 25)
    worker = threading.Thread(target=relay.tile, args=("mtg_fd:ir105_hrfi", None, bbox, 256, 256))
    worker.start()
    time.sleep(0.1)
    t0 = time.monotonic()
    with pytest.raises(WmsUpstreamError, match="busy"):
        relay.tile("mtg_fd:ir105_hrfi", None, tile_bbox(6, 33, 25), 256, 256)
    assert time.monotonic() - t0 < 1.0
    f.release.set()
    worker.join()


def test_upstream_failure_is_remembered_briefly(tmp_path: Path) -> None:
    now = [0.0]
    f = FakeFetcher()
    relay = WmsRelay(f, tmp_path, clock=lambda: now[0])
    relay.times("mtg_fd:ir105_hrfi", 1)
    f.fail = True
    with pytest.raises(WmsUpstreamError):
        relay.tile("mtg_fd:ir105_hrfi", None, tile_bbox(6, 32, 25), 256, 256)
    calls = len(f.calls)
    with pytest.raises(WmsUpstreamError, match="recently failed"):
        relay.tile("mtg_fd:ir105_hrfi", None, tile_bbox(6, 33, 25), 256, 256)
    assert len(f.calls) == calls  # failed fast, upstream not contacted
    f.fail, now[0] = False, 120.0
    relay.tile("mtg_fd:ir105_hrfi", None, tile_bbox(6, 33, 25), 256, 256)


def test_stale_capabilities_survive_a_failed_refresh(tmp_path: Path) -> None:
    now = [0.0]
    f = FakeFetcher()
    relay = WmsRelay(f, tmp_path, clock=lambda: now[0])
    first = relay.times("mtg_fd:ir105_hrfi", 1)
    f.fail, now[0] = True, 1000.0
    assert relay.times("mtg_fd:ir105_hrfi", 1) == first


def test_disk_cache_is_bounded_and_expires(tmp_path: Path) -> None:
    f = FakeFetcher()
    cache = tmp_path / "cache"
    relay = WmsRelay(f, cache, max_files=3)
    for x in range(5):
        relay.tile("mtg_fd:ir105_hrfi", None, tile_bbox(6, 30 + x, 25), 256, 256)
    assert len(list(cache.glob("*.png"))) == 3
    old = time.time() - 2 * 86400
    for png in cache.glob("*.png"):
        os.utime(png, (old, old))
    getmaps = len([u for u in f.calls if "GetMap" in u])
    relay.tile("mtg_fd:ir105_hrfi", None, tile_bbox(6, 34, 25), 256, 256)
    assert len([u for u in f.calls if "GetMap" in u]) == getmaps + 1  # expired entry fetched again
