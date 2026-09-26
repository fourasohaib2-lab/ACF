"""Observation API: aerodromes at a time, aerodrome detail vs model, SIGMET, verification report."""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from acf.awci.obs.source_awc import AwcClient
from acf.awci.obs.store import ObsStore
from acf.awci.ops.engine import DEFAULT_OPERATIONAL_PROFILE_PATH, load_profile
from acf.awci.ops.ingest import ingest_run
from acf.web.awci_app import create_awci_app
from tests.awci_ops_support import DOMAIN, FixtureFetcher

AWC = Path(__file__).parent / "data" / "awc"
RUN = datetime(2026, 9, 25, 0, tzinfo=UTC)
DOMAINS = ('{"domains": [{"name": "fixture", "label": "f", "south": 35, "north": 37, "west": 2, "east": 4, "default": true},'
           ' {"name": "empty", "label": "e", "south": 10, "north": 12, "west": 2, "east": 4}]}')
DAAG = {"icao": "DAAG", "name": "Algiers Intl", "lat": 36.691, "lon": 3.215, "elev_m": 18.0, "metar": True, "taf": True}


@pytest.fixture(scope="module")
def client(tmp_path_factory: pytest.TempPathFactory) -> TestClient:
    root = tmp_path_factory.mktemp("obsapi")
    ingest_run(RUN, [DOMAIN], load_profile(DEFAULT_OPERATIONAL_PROFILE_PATH), FixtureFetcher(), root, [0, 3])
    store = ObsStore(root, "fixture")
    store.write_stations([DAAG], datetime(2026, 9, 26, tzinfo=UTC))
    store.add_metars([r for r in map(AwcClient._metar, json.loads((AWC / "metar_daag_20260925.json").read_text())) if r])
    store.write_tafs([r for r in map(AwcClient._taf, json.loads((AWC / "taf_sample_20260926T08.json").read_text()))
                      if r and r["icao"] == "DAAG"])
    va = next(r for r in map(AwcClient._sigmet, json.loads((AWC / "isigmet_20260926T08.json").read_text()))
              if r and r["hazard"] == "VA")
    store.add_sigmets([va])
    store.write_status({"ingested_at": "2026-09-26T08:52:54Z", "stations": 1})
    domains = root / "domains.json"
    domains.write_text(DOMAINS)
    return TestClient(create_awci_app(data_dir=root, domains_file=domains))


def test_airports_at_a_valid_time(client: TestClient) -> None:
    body = client.get("/api/v1/awci/airports", params={"domain": "fixture", "time": "2026-09-25T03:00:00Z"}).json()
    assert body["ingested_at"] == "2026-09-26T08:52:54Z" and "Aviation Weather Center" in body["attribution"]
    (daag,) = body["airports"]
    obs = daag["observation"]
    assert daag["icao"] == "DAAG" and abs(datetime.fromisoformat(obs["time"].replace("Z", "+00:00"))
                                          - datetime(2026, 9, 25, 3, tzinfo=UTC)).total_seconds() <= 1800
    assert obs["raw"].startswith(("METAR DAAG", "SPECI DAAG")) and obs["flight_category"] in ("VFR", "MVFR", "IFR", "LIFR")
    assert {"ceiling_status", "ceiling_ft", "convective", "layers", "weather", "visibility_m"} <= set(obs)


def test_airports_without_a_report_near_the_time(client: TestClient) -> None:
    body = client.get("/api/v1/awci/airports", params={"domain": "fixture", "time": "2026-09-20T03:00:00Z"}).json()
    assert body["airports"][0]["observation"] is None


def test_domain_without_observations_is_empty_not_an_error(client: TestClient) -> None:
    body = client.get("/api/v1/awci/airports", params={"domain": "empty"}).json()
    assert body["airports"] == [] and body["ingested_at"] is None


def test_airport_detail_pairs_observations_with_the_model(client: TestClient) -> None:
    r = client.get("/api/v1/awci/airport", params={"domain": "fixture", "icao": "DAAG", "run": "2026092500"})
    assert r.status_code == 200
    body = r.json()
    assert body["station"]["icao"] == "DAAG" and body["taf"]["raw"].startswith("TAF DAAG")
    assert [p["step"] for p in body["model"]] == [0, 3]
    assert {"ceiling_ft", "convective_class", "genus_low", "surface_height_m"} <= set(body["model"][0])
    assert len(body["pairs"]) == 2 and all(p["observation"]["raw"] for p in body["pairs"])
    assert body["metars"] and all("2026-09-24T23" <= m["time"] <= "2026-09-25T04:00:00Z" for m in body["metars"])
    assert body["dz_m"] == pytest.approx(18.0 - body["model"][0]["surface_height_m"])


@pytest.mark.parametrize("params,status", [
    ({"icao": "ZZZZ"}, 404), ({"icao": "../x"}, 422), ({"run": "2026010100"}, 404), ({"domain": "nope"}, 404),
])
def test_airport_errors(client: TestClient, params: dict, status: int) -> None:
    base = {"domain": "fixture", "icao": "DAAG", "run": "2026092500"}
    assert client.get("/api/v1/awci/airport", params=base | params).status_code == status


def test_sigmets_valid_at_a_time_as_geojson(client: TestClient) -> None:
    during = client.get("/api/v1/awci/sigmets", params={"domain": "fixture", "time": "2026-09-26T05:00:00Z"}).json()
    (feature,) = during["features"]
    assert feature["geometry"]["type"] == "Polygon" and feature["properties"]["hazard"] == "VA"
    ring = feature["geometry"]["coordinates"][0]
    assert ring[0] == ring[-1]  # closed ring
    after = client.get("/api/v1/awci/sigmets", params={"domain": "fixture", "time": "2026-09-26T12:00:00Z"}).json()
    assert after["features"] == []


def test_verification_report_is_computed_and_cached(client: TestClient) -> None:
    first = client.get("/api/v1/awci/verification", params={"domain": "fixture", "run": "2026092500"}).json()
    assert first["run"] == "2026092500" and first["pairs"] == 2
    assert set(first["events"]) == {"ceiling_below_500ft", "ceiling_below_1000ft", "ceiling_below_1500ft", "convective"}
    again = client.get("/api/v1/awci/verification", params={"domain": "fixture", "run": "2026092500"}).json()
    assert again["generated_at"] == first["generated_at"]


def test_bad_time_is_rejected(client: TestClient) -> None:
    assert client.get("/api/v1/awci/airports", params={"domain": "fixture", "time": "demain"}).status_code == 422
