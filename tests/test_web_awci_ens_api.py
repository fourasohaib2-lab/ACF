"""ENS API: runs, manifest, probability fields (count / n, never over n = 0) and point series."""

from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pytest
from fastapi.testclient import TestClient

from acf.awci.ops.ens_ingest import ingest_ens_run
from acf.awci.ops.ens_store import EnsStore
from acf.web.awci_app import create_awci_app
from tests.awci_ops_support import DOMAIN, ENS_FIXTURE, FixtureFetcher

DOMAINS = '{"domains": [{"name": "fixture", "label": "f", "south": 35, "north": 37, "west": 2, "east": 4, "default": true}]}'


@pytest.fixture(scope="module")
def setup(tmp_path_factory: pytest.TempPathFactory) -> tuple[TestClient, Path]:
    root = tmp_path_factory.mktemp("ensapi")
    ingest_ens_run(datetime(2026, 9, 26, tzinfo=UTC), DOMAIN, FixtureFetcher(root=ENS_FIXTURE), root, steps=[0, 6, 12],
                   members=[1, 2, 3, 4])
    domains = root / "domains.json"
    domains.write_text(DOMAINS)
    return TestClient(create_awci_app(data_dir=root, domains_file=domains)), root


def test_runs_and_meta(setup: tuple[TestClient, Path]) -> None:
    client, _ = setup
    runs = client.get("/api/v1/awci/ens/runs", params={"domain": "fixture"}).json()
    assert runs[0]["run"] == "2026092600" and runs[0]["missing_steps"] == [12]
    meta = client.get("/api/v1/awci/ens/meta", params={"domain": "fixture", "run": "2026092600"}).json()
    assert meta["members_used"] == {"0": 4, "6": 4} and "p_awci_high" in meta["products"]
    assert "IFS ENS" in meta["attribution"]


def test_probability_field_is_count_over_n(setup: tuple[TestClient, Path]) -> None:
    client, root = setup
    r = client.get("/api/v1/awci/ens/field", params={"domain": "fixture", "run": "2026092600", "product": "p_cloud_bkn",
                                                     "step": 6, "level": 850})
    assert r.status_code == 200 and r.headers["x-awci-unit"] == "probability"
    ny, nx = (int(x) for x in r.headers["x-awci-shape"].split(","))
    values = np.frombuffer(r.content, dtype="<f4").reshape(ny, nx)
    ds = EnsStore(root).dataset("fixture", "2026092600")
    li = list(ds["level"].values).index(850.0)
    count = ds["p_cloud_bkn_count"].isel(step=1, level=li).values.astype(float)
    n = ds["p_cloud_bkn_n"].isel(step=1, level=li).values.astype(float)
    expected = np.where(n > 0, count / np.where(n > 0, n, 1), np.nan)
    np.testing.assert_allclose(values, expected)
    assert set(np.unique(values[np.isfinite(values)])) <= {0, 0.25, 0.5, 0.75, 1.0}  # 4 members


def test_surface_product_and_statistics(setup: tuple[TestClient, Path]) -> None:
    client, _ = setup
    base = {"domain": "fixture", "run": "2026092600", "step": 0}
    assert client.get("/api/v1/awci/ens/field", params=base | {"product": "p_convection"}).status_code == 200
    r = client.get("/api/v1/awci/ens/field", params=base | {"product": "awci_std", "level": 300})
    assert r.status_code == 200 and r.headers["x-awci-unit"] == "AWCI (0-100)"


@pytest.mark.parametrize("params,status", [
    ({"product": "p_cloud_bkn", "step": 12, "level": 850}, 404),   # step not computed
    ({"product": "p_cloud_bkn", "step": 3, "level": 850}, 404),    # not an ENS step
    ({"product": "p_cloud_bkn", "step": 6}, 422),                  # level product without level
    ({"product": "p_cloud_bkn", "step": 6, "level": 333}, 404),    # unknown level
    ({"product": "evil", "step": 6}, 422),
])
def test_field_errors(setup: tuple[TestClient, Path], params: dict, status: int) -> None:
    client, _ = setup
    r = client.get("/api/v1/awci/ens/field", params={"domain": "fixture", "run": "2026092600"} | params)
    assert r.status_code == status


def test_point_series(setup: tuple[TestClient, Path]) -> None:
    client, _ = setup
    body = client.get("/api/v1/awci/ens/point", params={"domain": "fixture", "run": "2026092600", "lat": 36.5,
                                                        "lon": 3.0, "level": 850}).json()
    assert [p["step"] for p in body["points"]] == [0, 6, 12]
    first, missing = body["points"][0], body["points"][2]
    assert missing["missing"] is True and missing["probabilities"] is None
    assert first["members"] == 4 and set(first["probabilities"]) >= {"p_awci_high", "p_convection", "p_ceiling_1500ft"}
    assert all(v is None or 0 <= v <= 1 for v in first["probabilities"].values())
    assert first["awci_std"] is None or first["awci_std"] >= 0


def test_unknown_run_is_404(setup: tuple[TestClient, Path]) -> None:
    client, _ = setup
    assert client.get("/api/v1/awci/ens/meta", params={"domain": "fixture", "run": "2020010100"}).status_code == 404
