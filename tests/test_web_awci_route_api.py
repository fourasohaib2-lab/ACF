"""Route API (SP4): cross-section equal to the cube at the nearest cells, relief, meteogram, input refusals."""

from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pytest
from fastapi.testclient import TestClient

from acf.awci.ops.engine import DEFAULT_OPERATIONAL_PROFILE_PATH, load_profile
from acf.awci.ops.ingest import ingest_run
from acf.awci.ops.store import CubeStore
from acf.web.awci_app import create_awci_app
from tests.awci_ops_support import DOMAIN, FixtureFetcher

RUN = datetime(2026, 9, 25, 0, tzinfo=UTC)
BASE = "/api/v1/awci"
ROUTE = "35.3,2.2;36.69,3.21;36.9,3.9"  # south-west of the crop, Algiers (DAAG), north-east
Q = {"domain": "fixture", "run": "2026092500", "points": ROUTE}


@pytest.fixture(scope="module")
def setup(tmp_path_factory: pytest.TempPathFactory) -> tuple[TestClient, Path]:
    root = tmp_path_factory.mktemp("route")
    ingest_run(RUN, [DOMAIN], load_profile(DEFAULT_OPERATIONAL_PROFILE_PATH), FixtureFetcher(fail_steps=(3,)),
               root, [0, 3])
    (root / "domains.json").write_text('{"domains": [{"name": "fixture", "label": "f", "south": 35, "north": 37, '
                                       '"west": 2, "east": 4, "default": true}]}')
    return TestClient(create_awci_app(data_dir=root, domains_file=root / "domains.json")), root


def _cells(ds, lat: list[float], lon: list[float]) -> tuple[np.ndarray, np.ndarray]:
    ii = np.array([int(np.abs(ds["lat"].values - v).argmin()) for v in lat])
    jj = np.array([int(np.abs(ds["lon"].values - v).argmin()) for v in lon])
    return ii, jj


@pytest.mark.parametrize("layer", ["awci", "cloud_fraction", "wind_speed"])
def test_section_is_the_cube_at_the_nearest_cells(setup: tuple[TestClient, Path], layer: str) -> None:
    client, root = setup
    body = client.get(f"{BASE}/route/section", params=Q | {"step": 0, "layer": layer}).json()
    ds = CubeStore(root).dataset("fixture", "2026092500")
    ii, jj = _cells(ds, body["lat"], body["lon"])
    cube = ds[layer].isel(step=0).values[:, ii, jj]
    values = np.array([[np.nan if v is None else v for v in row] for row in body["values"]])
    assert values.shape == (len(body["levels_hpa"]), len(body["distance_km"]))
    np.testing.assert_allclose(values, cube, equal_nan=True)  # null exactly where the cube has no value
    assert body["grid_lat"] == ds["lat"].values[ii].tolist()
    assert np.diff(body["distance_km"]).max() <= 10.01 and len(body["waypoints"]) == 3
    assert body["waypoints"][1]["lat"] == pytest.approx(36.69) and body["provenance"]["step"] == 0
    sp = np.array(body["surface_pressure_hpa"], dtype=float)
    np.testing.assert_allclose(sp, ds["sp_hpa"].isel(step=0).values[ii, jj])


def test_levels_under_the_model_surface_have_no_value(setup: tuple[TestClient, Path]) -> None:
    client, _ = setup
    body = client.get(f"{BASE}/route/section", params=Q | {"step": 0, "layer": "awci"}).json()
    for li, p in enumerate(body["levels_hpa"]):
        for k, sp in enumerate(body["surface_pressure_hpa"]):
            if sp is not None and p > sp:  # pressure level below the ground
                assert body["values"][li][k] is None


def test_meteogram_is_the_route_statistics_per_step_and_level(setup: tuple[TestClient, Path]) -> None:
    client, root = setup
    body = client.get(f"{BASE}/route/meteogram", params=Q).json()
    assert [s["step"] for s in body["steps"]] == [0, 3] and body["steps"][1]["missing"] is True
    assert body["steps"][1]["awci_max"] is None
    ds = CubeStore(root).dataset("fixture", "2026092500")
    ii, jj = _cells(ds, body["lat"], body["lon"])
    awci = ds["awci"].isel(step=0).values[:, ii, jj]
    first = body["steps"][0]
    for li in range(len(body["levels_hpa"])):
        row = awci[li][np.isfinite(awci[li])]
        if row.size:
            assert first["awci_max"][li] == pytest.approx(row.max())
            assert first["frac_awci_high"][li] == pytest.approx((row >= body["awci_high_lower_bound"]).mean())
        else:
            assert first["awci_max"][li] is None and first["frac_awci_high"][li] is None
    assert body["awci_high_lower_bound"] == 50
    assert all(v is None or 0 <= v <= 1 for v in first["frac_cloud_bkn"])


@pytest.mark.parametrize("params,status", [
    ({"step": 0, "layer": "awci", "points": "36,3;38,3"}, 400),        # leaves the domain
    ({"step": 0, "layer": "awci", "points": "36,3"}, 400),             # one point
    ({"step": 0, "layer": "awci", "points": "36,3;x,3"}, 400),
    ({"step": 0, "layer": "ceiling_m", "points": ROUTE}, 400),         # surface layer: no section
    ({"step": 3, "layer": "awci", "points": ROUTE}, 404),              # missing step
    ({"step": 0, "layer": "awci", "points": ";".join(["36,3"] * 200)}, 422),  # longer than the query limit
])
def test_refusals(setup: tuple[TestClient, Path], params: dict, status: int) -> None:
    client, _ = setup
    r = client.get(f"{BASE}/route/section", params={"domain": "fixture", "run": "2026092500"} | params)
    assert r.status_code == status
    if params.get("points") == "36,3;38,3":
        assert "leaves domain" in r.json()["detail"]
