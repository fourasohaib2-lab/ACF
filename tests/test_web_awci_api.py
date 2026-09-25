import struct
from datetime import UTC, datetime

import numpy as np
import pytest
from fastapi.testclient import TestClient

from acf.awci.ops.engine import DEFAULT_OPERATIONAL_PROFILE_PATH, load_profile
from acf.awci.ops.ingest import ingest_run
from acf.web.awci_app import create_awci_app
from tests.awci_ops_support import DOMAIN, FixtureFetcher

RUN = datetime(2026, 9, 25, 0, tzinfo=UTC)


@pytest.fixture(scope="module")
def client(tmp_path_factory) -> TestClient:
    root = tmp_path_factory.mktemp("awci")
    ingest_run(RUN, [DOMAIN], load_profile(DEFAULT_OPERATIONAL_PROFILE_PATH), FixtureFetcher(fail_steps=(3,)),
               root, [0, 3])
    domains = root / "domains.json"
    domains.write_text('{"domains": [{"name": "fixture", "label": "f", "south": 35, "north": 37, '
                       '"west": 2, "east": 4, "default": true}]}')
    return TestClient(create_awci_app(data_dir=root, domains_file=domains))


BASE = "/api/v1/awci"
Q = "domain=fixture&run=2026092500"


def test_domains_and_runs(client: TestClient) -> None:
    assert client.get(f"{BASE}/domains").json()[0]["name"] == "fixture"
    runs = client.get(f"{BASE}/runs?domain=fixture").json()
    assert runs[0]["run"] == "2026092500" and runs[0]["status"] == "partial"


def test_meta_has_flight_levels_and_provenance(client: TestClient) -> None:
    meta = client.get(f"{BASE}/meta?{Q}").json()
    assert meta["flight_levels"][meta["levels_hpa"].index(300.0)] == 301
    assert meta["provenance"]["license"] == "CC-BY-4.0" and meta["source_tier"] == "nwp_forecast"


def test_field_json_uses_null_for_missing(client: TestClient) -> None:
    body = client.get(f"{BASE}/field?{Q}&layer=awci&step=0&level=300").json()
    assert len(body["values"]) == 9 and len(body["values"][0]) == 9
    assert body["provenance"]["step"] == 0 and body["unit"] == "0-100"
    flat = [v for row in body["values"] for v in row]
    assert all(v is None or 0 <= v <= 100 for v in flat)


def test_field_binary_f32(client: TestClient) -> None:
    r = client.get(f"{BASE}/field?{Q}&layer=mucape&step=0&format=f32")
    assert r.headers["content-type"] == "application/octet-stream"
    assert r.headers["x-awci-shape"] == "9,9"
    values = struct.unpack("<81f", r.content)
    assert all(np.isnan(v) or v >= 0 for v in values)


def test_point_breakdown(client: TestClient) -> None:
    body = client.get(f"{BASE}/point?{Q}&step=0&level=300&lat=36.0&lon=3.0").json()
    assert body["lat"] == 36.0 and body["lon"] == 3.0
    assert set(body["modules"]) >= {"dynamic", "thermodynamic", "convective", "microphysical", "topographic"}
    assert body["excluded_modules"] == ["temporal", "confidence"]
    assert body["awci_level"] in {"Very Low", "Low", "Moderate", "High", "Very High", "Extreme", None}


def test_profile_and_timeseries(client: TestClient) -> None:
    prof = client.get(f"{BASE}/profile?{Q}&step=0&lat=36&lon=3").json()
    assert len(prof["levels"]) == 12
    ts = client.get(f"{BASE}/timeseries?{Q}&level=300&lat=36&lon=3").json()
    assert [p["step"] for p in ts["points"]] == [0, 3] and ts["points"][1]["awci"] is None


def test_registry(client: TestClient) -> None:
    body = client.get(f"{BASE}/registry").json()
    assert body["layers"]["cat_ti2"]["status"] == "HYPOTHESIS"
    assert body["classes"][0] == {"upper_bound": 20.0, "label": "Very Low"}
    assert body["profile"]["name"] == "operational-v1"


# Review Focus 1 and 2
def test_point_outside_domain_is_400(client: TestClient) -> None:
    assert client.get(f"{BASE}/point?{Q}&step=0&level=300&lat=50&lon=3").status_code == 400


def test_missing_step_of_partial_run_is_404(client: TestClient) -> None:
    r = client.get(f"{BASE}/field?{Q}&layer=awci&step=3&level=300")
    assert r.status_code == 404 and "3" in r.json()["detail"]


@pytest.mark.parametrize("query", ["layer=nope&step=0", "layer=awci&step=5&level=300", "layer=awci&step=0&level=333",
                                   "layer=awci&step=0"])
def test_invalid_parameters_are_400(client: TestClient, query: str) -> None:
    assert client.get(f"{BASE}/field?{Q}&{query}").status_code == 400


def test_unknown_run_is_404(client: TestClient) -> None:
    assert client.get(f"{BASE}/meta?domain=fixture&run=2026010100").status_code == 404


def test_router_mounted_in_main_app() -> None:
    from acf.web.hpc_dashboard_server import create_app

    app = create_app(hpc=object(), fno_checkpoint_path=None, event_db_path=":memory:", dataset_db_path=":memory:")
    assert TestClient(app).get("/api/v1/awci/registry").status_code == 200


def test_point_profile_timeseries_never_load_whole_variables(client: TestClient, monkeypatch) -> None:
    """Regression: reading one column must not decompress entire (step, level, lat, lon) variables."""
    import xarray as xr

    sizes: list[int] = []
    original = xr.DataArray.values

    def spy(self):  # noqa: ANN001, ANN202
        out = original.fget(self)
        sizes.append(int(np.asarray(out).size))
        return out

    monkeypatch.setattr(xr.DataArray, "values", property(spy))
    for url in (f"{BASE}/point?{Q}&step=0&level=300&lat=36&lon=3", f"{BASE}/profile?{Q}&step=0&lat=36&lon=3",
                f"{BASE}/timeseries?{Q}&level=300&lat=36&lon=3"):
        sizes.clear()
        assert client.get(url).status_code == 200
        assert max(sizes) <= 12, f"{url} materialized an array of {max(sizes)} values"
