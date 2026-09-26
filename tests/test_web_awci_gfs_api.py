"""SP6 API: model=gfs on the cube routes, IFS-GFS comparison equal to the cubes, refusals, GFS verification."""

import json
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pytest
from fastapi.testclient import TestClient

from acf.awci.obs.source_awc import AwcClient
from acf.awci.obs.store import ObsStore
from acf.awci.ops.domains import Domain
from acf.awci.ops.engine import DEFAULT_OPERATIONAL_PROFILE_PATH, load_profile
from acf.awci.ops.ingest import ingest_run
from acf.awci.ops.store import CubeStore
from acf.web.awci_app import create_awci_app
from acf.web.awci_compare import agreement
from tests.awci_ops_support import DOMAIN, FixtureFetcher, GfsFixtureFetcher

RUN = datetime(2026, 9, 25, tzinfo=UTC)
BASE = "/api/v1/awci"
AWC = Path(__file__).parent / "data" / "awc"
DOMAINS = '{"domains": [{"name": "fixture", "label": "f", "south": 35, "north": 37, "west": 2, "east": 4, "default": true}]}'
Q = {"domain": "fixture", "run": "2026092500"}


def _ingest(root: Path, gfs_domain: Domain = DOMAIN) -> TestClient:
    profile = load_profile(DEFAULT_OPERATIONAL_PROFILE_PATH)
    ingest_run(RUN, [DOMAIN], profile, FixtureFetcher(), root, [0, 3])
    ingest_run(RUN, [gfs_domain], profile, GfsFixtureFetcher(), root / "gfs", [0, 3, 6], model="gfs")
    (root / "domains.json").write_text(DOMAINS)
    return TestClient(create_awci_app(data_dir=root, domains_file=root / "domains.json"))


@pytest.fixture(scope="module")
def setup(tmp_path_factory: pytest.TempPathFactory) -> tuple[TestClient, Path]:
    root = tmp_path_factory.mktemp("gfsapi")
    client = _ingest(root)
    store = ObsStore(root, "fixture")
    store.write_stations([{"icao": "DAAG", "name": "Algiers", "lat": 36.691, "lon": 3.215, "elev_m": 18.0,
                           "metar": True, "taf": True}], datetime(2026, 9, 26, tzinfo=UTC))
    store.add_metars([r for r in map(AwcClient._metar, json.loads((AWC / "metar_daag_20260925.json").read_text())) if r])
    return client, root


def _f32(r) -> np.ndarray:
    ny, nx = (int(x) for x in r.headers["x-awci-shape"].split(","))
    return np.frombuffer(r.content, dtype="<f4").reshape(ny, nx)


def test_model_parameter_selects_the_cubes(setup: tuple[TestClient, Path]) -> None:
    client, root = setup
    assert [r["steps"] for r in client.get(f"{BASE}/runs", params={"domain": "fixture", "model": "gfs"}).json()] == [[0, 3, 6]]
    assert client.get(f"{BASE}/runs", params={"domain": "fixture"}).json()[0]["steps"] == [0, 3]
    meta = client.get(f"{BASE}/meta", params=Q | {"model": "gfs"}).json()
    assert "NOAA" in meta["provenance"]["model"] and "domaine public" in meta["provenance"]["attribution"]
    r = client.get(f"{BASE}/field", params=Q | {"model": "gfs", "layer": "awci", "step": 3, "level": 500, "format": "f32"})
    assert r.headers["x-awci-attribution"] == "NOAA/NCEP GFS public domain"
    cube = CubeStore(root / "gfs").dataset("fixture", "2026092500")
    np.testing.assert_allclose(_f32(r), cube["awci"].isel(step=1, level=list(cube["level"].values).index(500)).values)
    assert client.get(f"{BASE}/meta", params=Q | {"model": "icon"}).status_code == 422


@pytest.mark.parametrize("product,layer,threshold,level", [
    ("agree_icing", "icing_potential", 1.0, 500), ("agree_cat", "cat_category", 2.0, 300),
    ("agree_convection", "convective_class", 2.0, None)])
def test_agreement_is_computed_from_the_two_cubes(setup: tuple[TestClient, Path], product: str, layer: str,
                                                   threshold: float, level: int | None) -> None:
    client, root = setup
    params = Q | {"step": 3, "product": product} | ({"level": level} if level else {})
    got = _f32(client.get(f"{BASE}/compare/field", params=params))
    ifs, gfs = CubeStore(root).dataset("fixture", "2026092500"), CubeStore(root / "gfs").dataset("fixture", "2026092500")
    sel = {"level": list(ifs["level"].values).index(level)} if level else {}
    np.testing.assert_array_equal(got, agreement(ifs[layer].isel(step=1, **sel).values, gfs[layer].isel(step=1, **sel).values,
                                                 threshold))
    assert set(np.unique(got[np.isfinite(got)])) <= {0, 1, 2, 3}


def test_awci_difference_and_point(setup: tuple[TestClient, Path]) -> None:
    client, root = setup
    diff = _f32(client.get(f"{BASE}/compare/field", params=Q | {"step": 3, "product": "awci_diff", "level": 500}))
    ifs, gfs = CubeStore(root).dataset("fixture", "2026092500"), CubeStore(root / "gfs").dataset("fixture", "2026092500")
    li = list(ifs["level"].values).index(500)
    np.testing.assert_allclose(diff, gfs["awci"].isel(step=1, level=li).values - ifs["awci"].isel(step=1, level=li).values,
                               rtol=1e-6)
    body = client.get(f"{BASE}/compare/point", params=Q | {"step": 3, "level": 500, "lat": 36.5, "lon": 3.0}).json()
    assert set(body["models"]) == {"ifs", "gfs"} and "r" in body["definition_differences"]
    a, b = body["models"]["ifs"]["values"]["awci"], body["models"]["gfs"]["values"]["awci"]
    assert body["awci_diff"] == pytest.approx(b - a)


@pytest.mark.parametrize("params,status,text", [
    ({"step": 6, "product": "awci_diff", "level": 500}, 404, "IFS run"),      # GFS has +6 h, IFS does not
    ({"step": 3, "product": "awci_diff"}, 422, "level"),
    ({"step": 3, "product": "nope", "level": 500}, 422, ""),
])
def test_comparison_refusals(setup: tuple[TestClient, Path], params: dict, status: int, text: str) -> None:
    client, _ = setup
    r = client.get(f"{BASE}/compare/field", params=Q | params)
    assert r.status_code == status and text in r.text


def test_different_grids_are_refused_not_regridded(tmp_path: Path) -> None:
    client = _ingest(tmp_path, Domain("fixture", "f", 35.25, 37.0, 2.0, 4.0, True))
    r = client.get(f"{BASE}/compare/field", params=Q | {"step": 3, "product": "awci_diff", "level": 500})
    assert r.status_code == 409 and "same grid" in r.text


def test_gfs_verification_uses_the_observation_archive_of_the_data_root(setup: tuple[TestClient, Path]) -> None:
    client, _ = setup
    body = client.get(f"{BASE}/verification", params=Q | {"model": "gfs"}).json()
    assert body["model_id"] == "gfs" and "NOAA GFS" in body["forecast"]
    assert body["events"]["convective"]["total"]["n"] >= 2  # DAAG at +0 and +3 h (+6 h also observed)
    assert client.get(f"{BASE}/verification", params=Q).json()["model_id"] == "ifs"
