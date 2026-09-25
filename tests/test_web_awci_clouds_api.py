"""SP1C API: /clouds, /volume, /terrain, registry codes, and cubes ingested before SP1C."""

import json
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pytest
import xarray as xr
from fastapi.testclient import TestClient

from acf.awci.ops.clouds import CLOUD_LEVEL_LAYERS, CLOUD_SURFACE_LAYERS
from acf.awci.ops.engine import DEFAULT_OPERATIONAL_PROFILE_PATH, load_profile
from acf.awci.ops.ingest import ingest_run
from acf.web.awci_app import create_awci_app
from tests.awci_ops_support import DOMAIN, FixtureFetcher

RUN = datetime(2026, 9, 25, 0, tzinfo=UTC)
DOMAINS = ('{"domains": [{"name": "fixture", "label": "f", "south": 35, "north": 37, '
           '"west": 2, "east": 4, "default": true}]}')
SP1C_ONLY = (*CLOUD_LEVEL_LAYERS, *CLOUD_SURFACE_LAYERS, "cloud_cover_bias", "cloud_top_teff_k", "column_condensate",
             "snowfall_mm", "snow_depth_cm", "freezing_precip_mm", "surface_height_m")


def _app(root: Path) -> TestClient:
    domains = root / "domains.json"
    domains.write_text(DOMAINS)
    return TestClient(create_awci_app(data_dir=root, domains_file=domains))


@pytest.fixture(scope="module")
def client(tmp_path_factory) -> TestClient:
    root = tmp_path_factory.mktemp("awci_clouds")
    ingest_run(RUN, [DOMAIN], load_profile(DEFAULT_OPERATIONAL_PROFILE_PATH), FixtureFetcher(), root, [0, 3])
    return _app(root)


@pytest.fixture(scope="module")
def old_client(tmp_path_factory) -> TestClient:
    """A cube as SP1 wrote it: no SP1C variables, manifest without them."""
    root = tmp_path_factory.mktemp("awci_sp1")
    ingest_run(RUN, [DOMAIN], load_profile(DEFAULT_OPERATIONAL_PROFILE_PATH), FixtureFetcher(), root, [0, 3])
    run_dir = root / "fixture" / "2026092500"
    with xr.open_dataset(run_dir / "cube.nc") as ds:
        old = ds.drop_vars(list(SP1C_ONLY)).load()
    old.to_netcdf(run_dir / "cube.nc")
    manifest = json.loads((run_dir / "manifest.json").read_text())
    manifest["level_layers"] = [n for n in manifest["level_layers"] if n not in SP1C_ONLY]
    manifest["surface_layers"] = [n for n in manifest["surface_layers"] if n not in SP1C_ONLY]
    for key in ("cloud_profile", "cloud_profile_version", "accumulation_interval_h", "cloud_consistency", "cloud_status"):
        manifest.pop(key, None)
    (run_dir / "manifest.json").write_text(json.dumps(manifest))
    return _app(root)


@pytest.fixture
def run_id() -> str:
    return "2026092500"


def test_clouds_point_payload(client, run_id) -> None:
    r = client.get("/api/v1/awci/clouds", params={"domain": "fixture", "run": run_id, "step": 3, "lat": 36, "lon": 3})
    assert r.status_code == 200
    body = r.json()
    assert body["metar"].startswith("MODEL ") and isinstance(body["layers"], list)
    assert set(body["cloud_covers"]) == {"low", "mid", "high", "total_diag"}
    assert body["scientific_status"]["cloud_genus"] == "HYPOTHESIS"
    assert body["provenance"]["attribution"] == "© ECMWF, CC-BY-4.0"


def test_volume_binary_layout(client, run_id) -> None:
    r = client.get("/api/v1/awci/volume", params={"domain": "fixture", "run": run_id, "step": 3,
                                                  "layer": "cloud_fraction", "stride": 2})
    assert r.status_code == 200
    nl, ny, nx = (int(x) for x in r.headers["X-AWCI-Shape"].split(","))
    assert (nl, ny, nx) == (12, 5, 5) and r.headers["X-AWCI-Parts"] == "values,gh"
    data = np.frombuffer(r.content, dtype="<f4")
    assert data.size == 2 * nl * ny * nx
    gh = data[nl * ny * nx:].reshape(nl, ny, nx)
    assert np.all(np.diff(gh, axis=0)[np.isfinite(np.diff(gh, axis=0))] > 0)


def test_volume_rejects_surface_layer_and_bad_stride(client, run_id) -> None:
    base = {"domain": "fixture", "run": run_id, "step": 3}
    assert client.get("/api/v1/awci/volume", params=base | {"layer": "tcc"}).status_code == 400
    assert client.get("/api/v1/awci/volume", params=base | {"layer": "cloud_fraction", "stride": 3}).status_code == 422


def test_terrain_f32(client, run_id) -> None:
    r = client.get("/api/v1/awci/terrain", params={"domain": "fixture", "run": run_id})
    assert r.status_code == 200 and len(r.content) == 9 * 9 * 4


def test_pre_sp1c_cube_still_served_and_clouds_404(old_client, run_id) -> None:
    ok = old_client.get("/api/v1/awci/point", params={"domain": "fixture", "run": run_id, "step": 3, "level": 850,
                                                      "lat": 36, "lon": 3})
    assert ok.status_code == 200 and "cloud_fraction" not in ok.json()["level_layers"]
    assert old_client.get("/api/v1/awci/clouds", params={"domain": "fixture", "run": run_id, "step": 3,
                                                         "lat": 36, "lon": 3}).status_code == 404
    assert old_client.get("/api/v1/awci/field", params={"domain": "fixture", "run": run_id, "step": 3,
                                                        "layer": "ceiling_m"}).status_code == 404
    assert old_client.get("/api/v1/awci/terrain", params={"domain": "fixture", "run": run_id}).status_code == 404


def test_registry_exposes_codes_and_cloud_profile(client) -> None:
    body = client.get("/api/v1/awci/registry").json()
    assert body["codes"]["genus"]["Cb"] == 9 and body["codes"]["clear"] == -1
    assert body["cloud_profile"]["name"] == "cloud-v1"


def test_clouds_over_sea_use_sea_level_not_bathymetry(tmp_path) -> None:
    from tests.awci_ops_support import WET_DOMAIN, WET_FIXTURE

    ingest_run(RUN, [WET_DOMAIN], load_profile(DEFAULT_OPERATIONAL_PROFILE_PATH), FixtureFetcher(root=WET_FIXTURE),
               tmp_path, [0, 3])
    domains = tmp_path / "domains.json"
    domains.write_text('{"domains": [{"name": "fixture_wet", "label": "w", "south": 15, "north": 17, '
                       '"west": -20, "east": -18, "default": true}]}')
    c = TestClient(create_awci_app(data_dir=tmp_path, domains_file=domains))
    q = {"domain": "fixture_wet", "run": "2026092500"}
    body = c.get("/api/v1/awci/clouds", params=q | {"step": 3, "lat": 16, "lon": -19}).json()
    assert abs(body["elevation_m"]) < 50.0
    assert all(lay["base_agl_m"] < 6000.0 for lay in body["layers"] if lay["kind"] == "layer")
    assert "CB" in body["metar"]
    terrain = np.frombuffer(c.get("/api/v1/awci/terrain", params=q).content, dtype="<f4")
    assert (np.abs(terrain) < 50.0).all()


def test_meta_and_clouds_expose_cloud_status_and_accumulation_interval(client, run_id) -> None:
    meta = client.get("/api/v1/awci/meta", params={"domain": "fixture", "run": run_id}).json()
    assert meta["cloud_status"] in ("ok", "degraded") and meta["accumulation_interval_h"] == [None, 3]
    assert [c["step"] for c in meta["cloud_consistency"]] == [0, 3] and meta["cloud_profile"]["name"] == "cloud-v1"
    body = client.get("/api/v1/awci/clouds", params={"domain": "fixture", "run": run_id, "step": 3, "lat": 36,
                                                     "lon": 3}).json()
    assert body["run_cloud_status"] == meta["cloud_status"] and body["accumulation_interval_h"] == 3
    assert body["step_consistency"]["step"] == 3


def test_meta_of_a_pre_sp1c_run_has_null_cloud_status(old_client, run_id) -> None:
    meta = old_client.get("/api/v1/awci/meta", params={"domain": "fixture", "run": run_id}).json()
    assert meta["cloud_status"] is None and meta["accumulation_interval_h"] is None
