"""AWC client (pagination past the 400-item cap, input validation), observation store and ingestion."""

import json
import urllib.parse
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from acf.awci.obs.ingest import main as ingest_main
from acf.awci.obs.source_awc import AWC_CAP, AwcClient, AwcError
from acf.awci.obs.store import ObsStore
from acf.awci.ops.domains import Domain

AWC = Path(__file__).parent / "data" / "awc"
STATIONS = json.loads((AWC / "stations_north_africa.json").read_text())
CORPUS = json.loads((AWC / "metar_corpus_20260926T08.json").read_text())
TAFS = json.loads((AWC / "taf_sample_20260926T08.json").read_text())
SIGMETS = json.loads((AWC / "isigmet_20260926T08.json").read_text())
DOMAIN = Domain("north_africa", "Afrique du Nord", 15.0, 45.0, -20.0, 40.0, True)


class FakeAwc:
    """Serves the recorded AWC responses and applies the real 400-item cap."""

    def __init__(self, fail: bool = False) -> None:
        self.urls: list[str] = []
        self.fail = fail

    def get(self, url: str, timeout: float) -> bytes:
        self.urls.append(url)
        if self.fail:
            raise OSError("AWC down")
        path = urllib.parse.urlparse(url).path.rsplit("/", 1)[-1]
        q = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(url).query))
        if path == "stationinfo":
            s, w, n, e = (float(v) for v in q["bbox"].split(","))
            items = [x for x in STATIONS if s <= x["lat"] <= n and w <= x["lon"] <= e]
        elif path == "metar":
            ids = set(q["ids"].split(","))
            items = [x for x in CORPUS if x["icaoId"] in ids]
        elif path == "taf":
            ids = set(q["ids"].split(","))
            items = [x for x in TAFS if x["icaoId"] in ids]
        elif path == "isigmet":
            items = SIGMETS
        else:
            raise AssertionError(url)
        return json.dumps(items[:AWC_CAP]).encode()


def test_stations_are_tiled_past_the_400_cap_and_validated() -> None:
    fake = FakeAwc()
    stations = AwcClient(fake).stations(DOMAIN)
    assert len(stations) == len(STATIONS) == 557  # one 400-capped request would lose 157
    assert all(len(s.icao) == 4 and s.metar for s in stations)
    assert len(fake.urls) > 1


def test_metars_are_batched_and_split_when_capped() -> None:
    fake = FakeAwc()
    ids = sorted({x["icaoId"] for x in CORPUS})
    records = AwcClient(fake, batch=500).metars(ids, hours=2)  # one batch would hit the cap -> split
    assert len(records) == len(CORPUS)
    assert all(r["raw"].startswith(("METAR", "SPECI")) and r["obs_time"].endswith("Z") for r in records)


def test_invalid_items_are_dropped_and_counted() -> None:
    class Bad(FakeAwc):
        def get(self, url: str, timeout: float) -> bytes:
            return json.dumps([{"icaoId": "DAAG", "obsTime": 1790411400, "rawOb": "METAR DAAG 260830Z VRB02KT CAVOK 26/17 Q1021",
                                "lat": 36.7, "lon": 3.2, "elev": 18},
                               {"icaoId": "../x", "obsTime": "soon", "rawOb": 3}, "junk"]).encode()
    client = AwcClient(Bad())
    assert len(client.metars(["DAAG"], hours=1)) == 1 and client.rejected == 2


def test_upstream_failures_raise() -> None:
    with pytest.raises(AwcError):
        AwcClient(FakeAwc(fail=True)).isigmets(DOMAIN)

    class NotJson(FakeAwc):
        def get(self, url: str, timeout: float) -> bytes:
            return b"<html>"
    with pytest.raises(AwcError):
        AwcClient(NotJson()).isigmets(DOMAIN)


def test_sigmets_are_kept_when_they_cross_the_domain() -> None:
    sig = AwcClient(FakeAwc()).isigmets(DOMAIN)
    assert sig and all(s["hazard"] in {"TS", "TURB", "ICE", "VA", "TC", "MTW"} for s in sig)
    for s in sig:
        lons = [c[0] for c in s["coords"]]
        lats = [c[1] for c in s["coords"]]
        assert max(lats) >= DOMAIN.south and min(lats) <= DOMAIN.north
        assert max(lons) >= DOMAIN.west and min(lons) <= DOMAIN.east


def _metar(icao: str, t: datetime, raw_tail: str = "VRB02KT CAVOK 26/17 Q1021") -> dict:
    return {"icao": icao, "obs_time": t.strftime("%Y-%m-%dT%H:%M:%SZ"), "raw": f"METAR {icao} {t:%d%H%M}Z {raw_tail}",
            "kind": "METAR", "lat": 36.7, "lon": 3.2, "elev_m": 18.0}


def test_store_deduplicates_by_utc_day_and_reads_windows(tmp_path: Path) -> None:
    store = ObsStore(tmp_path, "d")
    t0 = datetime(2026, 9, 25, 23, 30, tzinfo=UTC)
    batch = [_metar("DAAG", t0), _metar("DAAG", t0 + timedelta(minutes=30))]
    assert store.add_metars(batch) == 2
    assert store.add_metars(batch) == 0
    assert sorted(p.name for p in (tmp_path / ".obs" / "d" / "metar").iterdir()) == ["2026-09-25.jsonl", "2026-09-26.jsonl"]
    got = store.metars(t0 - timedelta(minutes=1), t0 + timedelta(hours=1))
    assert [r["obs_time"] for r in got] == ["2026-09-25T23:30:00Z", "2026-09-26T00:00:00Z"]


def test_store_retention_and_sigmets_valid_at(tmp_path: Path) -> None:
    store = ObsStore(tmp_path, "d")
    old = datetime(2026, 9, 1, tzinfo=UTC)
    store.add_metars([_metar("DAAG", old)])
    sig = {"hazard": "VA", "raw": "WVXX SIGMET A1", "valid_from": "2026-09-26T03:00:00Z", "valid_to": "2026-09-26T09:00:00Z",
           "received": "2026-09-26T03:05:00Z", "coords": [[0, 30], [1, 30], [1, 31], [0, 30]]}
    assert store.add_sigmets([sig, sig]) == 1
    assert len(store.sigmets_at(datetime(2026, 9, 26, 5, tzinfo=UTC))) == 1
    assert store.sigmets_at(datetime(2026, 9, 26, 9, tzinfo=UTC)) == []  # validity end is exclusive
    removed = store.apply_retention(days=10, now=datetime(2026, 9, 26, tzinfo=UTC))
    assert removed == ["metar/2026-09-01.jsonl"]


def test_ingest_command_end_to_end(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    domains = tmp_path / "domains.json"
    domains.write_text(json.dumps({"domains": [{"name": "north_africa", "label": "NA", "south": 15, "north": 45,
                                                "west": -20, "east": 40, "default": True}]}))
    fake = FakeAwc()
    monkeypatch.setattr("acf.awci.obs.ingest.UrllibAwcFetcher", lambda: fake)
    assert ingest_main(["--domain", "north_africa", "--domains-file", str(domains), "--data-dir", str(tmp_path),
                        "--hours", "2"]) == 0
    store = ObsStore(tmp_path, "north_africa")
    assert len(store.stations()) == 557
    status = store.status()
    catalogued = {s["icaoId"] for s in STATIONS}  # HLMS reports METAR but stationinfo does not list it as a METAR site
    assert status["metars_added"] == sum(i["icaoId"] in catalogued for i in CORPUS) == 399
    assert status["tafs"] == len(TAFS) and status["sigmets_added"] > 0
    assert status["ingested_at"].endswith("Z")
    # a second pass adds nothing and does not refetch the fresh station list
    n = len(fake.urls)
    assert ingest_main(["--domain", "north_africa", "--domains-file", str(domains), "--data-dir", str(tmp_path)]) == 0
    assert store.status()["metars_added"] == 0
    assert not any("stationinfo" in u for u in fake.urls[n:])


def test_ingest_reports_an_upstream_outage(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    domains = tmp_path / "domains.json"
    domains.write_text(json.dumps({"domains": [{"name": "d", "label": "d", "south": 35, "north": 37, "west": 2,
                                                "east": 4, "default": True}]}))
    monkeypatch.setattr("acf.awci.obs.ingest.UrllibAwcFetcher", lambda: FakeAwc(fail=True))
    assert ingest_main(["--domain", "d", "--domains-file", str(domains), "--data-dir", str(tmp_path)]) == 1
