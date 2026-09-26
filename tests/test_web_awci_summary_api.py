"""SP2 API additions: /summary, /summary/series, /clouds/series, dewpoint, ingestion time, etage bounds."""

from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from acf.awci.ops.engine import DEFAULT_OPERATIONAL_PROFILE_PATH, load_profile
from acf.awci.ops.ingest import ingest_run
from acf.web.awci_app import create_awci_app
from tests.awci_ops_support import DOMAIN, FixtureFetcher

RUN = datetime(2026, 9, 25, 0, tzinfo=UTC)
BASE = "/api/v1/awci"
Q = {"domain": "fixture", "run": "2026092500"}


@pytest.fixture(scope="module")
def client(tmp_path_factory) -> TestClient:
    root = tmp_path_factory.mktemp("awci_summary")
    ingest_run(RUN, [DOMAIN], load_profile(DEFAULT_OPERATIONAL_PROFILE_PATH), FixtureFetcher(), root, [0, 3])
    domains = root / "domains.json"
    domains.write_text('{"domains": [{"name": "fixture", "label": "f", "south": 35, "north": 37, '
                       '"west": 2, "east": 4, "default": true}]}')
    return TestClient(create_awci_app(data_dir=root, domains_file=domains))


def test_summary_route(client) -> None:
    body = client.get(f"{BASE}/summary", params=Q | {"step": 3, "level": 300}).json()
    for key in ("awci_p95", "awci_class", "turbulence_area_pct", "icing_area_pct", "shear_p95", "low_ceiling_area_pct",
                "cb_area_pct", "valid_cells_pct", "badges", "awci_p95_by_level", "provenance"):
        assert key in body
    assert len(body["awci_p95_by_level"]) == 12 and body["provenance"]["step"] == 3


def test_summary_series_route(client) -> None:
    body = client.get(f"{BASE}/summary/series", params=Q | {"level": 300}).json()
    assert [p["step"] for p in body["points"]] == [0, 3] and "awci_p95" in body["points"][0]


def test_clouds_series_route(client) -> None:
    body = client.get(f"{BASE}/clouds/series", params=Q | {"lat": 36, "lon": 3}).json()
    assert [p["step"] for p in body["points"]] == [0, 3]
    assert set(body["points"][0]["genus"]) == {"low", "mid", "high"}


def test_profile_has_dewpoint_not_above_temperature(client) -> None:
    levels = client.get(f"{BASE}/profile", params=Q | {"step": 3, "lat": 36, "lon": 3}).json()["levels"]
    for lev in levels:
        t, td = lev["level_layers"].get("t"), lev["dewpoint_k"]
        assert (t is None) == (td is None) and (td is None or td <= t + 1e-6)


def test_runs_expose_ingestion_time(client) -> None:
    assert client.get(f"{BASE}/runs", params={"domain": "fixture"}).json()[0]["ingested_at"]


def test_clouds_etage_bounds_and_base_fl(client) -> None:
    body = client.get(f"{BASE}/clouds", params=Q | {"step": 3, "lat": 36, "lon": 3}).json()
    b = body["etage_bounds_fl"]
    assert b["mid_high"] > b["low_mid"] > 0
    assert all("base_fl" in lay for lay in body["layers"] if lay["kind"] == "layer")
