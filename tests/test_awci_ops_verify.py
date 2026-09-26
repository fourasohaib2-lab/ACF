"""Cloud verification against METAR: scores, time matching, exclusions, real DAAG case on the IFS fixture."""

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import numpy as np
import pytest
import xarray as xr

from acf.awci.obs.source_awc import AwcClient
from acf.awci.ops.engine import DEFAULT_OPERATIONAL_PROFILE_PATH, load_profile
from acf.awci.ops.ingest import ingest_run
from acf.awci.ops.verify import (
    ModelAtStations,
    VerifyConfig,
    build_pairs,
    match_reports,
    model_at_stations,
    scores,
    verify_run,
)
from tests.awci_ops_support import DOMAIN, FixtureFetcher

RUN = datetime(2026, 9, 25, 0, tzinfo=UTC)
DAAG_METARS = json.loads((Path(__file__).parent / "data" / "awc" / "metar_daag_20260925.json").read_text())


def test_scores_on_a_hand_computed_table() -> None:
    s = scores(30, 20, 10, 940)
    assert s["n"] == 1000 and s["pod"] == pytest.approx(0.75) and s["far"] == pytest.approx(0.4)
    assert s["csi"] == pytest.approx(0.5) and s["bias"] == pytest.approx(1.25)
    assert s["ets"] == pytest.approx(28 / 58)  # a_r = 50 * 40 / 1000 = 2
    assert s["observed_events"] == 40 and s["sufficient"] is True


def test_undefined_scores_are_null_and_small_samples_flagged() -> None:
    s = scores(0, 0, 0, 12)
    assert s["pod"] is None and s["far"] is None and s["csi"] is None and s["bias"] is None and s["ets"] is None
    assert scores(3, 1, 2, 50)["sufficient"] is False


def _rec(t: datetime, kind: str = "METAR", tail: str = "CAVOK 20/10 Q1015") -> dict:
    return {"icao": "DAAG", "obs_time": t.strftime("%Y-%m-%dT%H:%M:%SZ"), "kind": kind,
            "raw": f"{kind} DAAG {t:%d%H%M}Z 00000KT {tail}"}


def test_nearest_report_within_tolerance() -> None:
    t = datetime(2026, 9, 25, 3, tzinfo=UTC)
    recs = [_rec(t - timedelta(minutes=40)), _rec(t + timedelta(minutes=20)), _rec(t - timedelta(minutes=10), "SPECI"),
            _rec(t + timedelta(minutes=10))]
    got = match_reports(recs, [t, t + timedelta(hours=3)], timedelta(minutes=30))
    assert got[0]["obs_time"] == "2026-09-25T03:10:00Z"  # 10 min either side: the routine METAR wins over SPECI
    assert got[1] is None  # nothing within 30 min of 06Z


def _model(ceiling_m: list[list[float]], conv: list[list[float]], sfc: list[list[float]]) -> ModelAtStations:
    t0 = datetime(2026, 9, 25, 0, tzinfo=UTC)
    return ModelAtStations(steps=[0, 30], valid_times=[t0, t0 + timedelta(hours=30)], missing_steps=[],
                           icao=["AAAA", "BBBB"], grid_lat=[36.0, 36.0], grid_lon=[3.0, 3.25],
                           ceiling_m=np.array(ceiling_m), convective_class=np.array(conv),
                           surface_height_m=np.array(sfc))


def test_pairs_events_and_exclusions() -> None:
    stations = [{"icao": "AAAA", "name": "A", "lat": 36.0, "lon": 3.0, "elev_m": 10.0},
                {"icao": "BBBB", "name": "B", "lat": 36.0, "lon": 3.25, "elev_m": 900.0}]
    metars = [
        {"icao": "AAAA", "obs_time": "2026-09-25T00:00:00Z", "kind": "METAR", "raw": "METAR AAAA 250000Z 00000KT 2000 BR BKN004 15/14 Q1015"},
        {"icao": "AAAA", "obs_time": "2026-09-26T06:00:00Z", "kind": "METAR", "raw": "METAR AAAA 260600Z 00000KT 9999 FEW030CB 25/14 Q1015"},
        {"icao": "BBBB", "obs_time": "2026-09-25T00:00:00Z", "kind": "METAR", "raw": "METAR BBBB 250000Z 00000KT 9999 SCT030TCU 15/10 Q1015"},
        {"icao": "BBBB", "obs_time": "2026-09-26T06:00:00Z", "kind": "METAR", "raw": "METAR BBBB 26060"},  # undecodable
    ]
    # AAAA: model ceiling 120 m = 394 ft at step 0, no ceiling at step 30; BBBB: model surface 100 m vs 900 m station
    model = _model([[120.0, 300.0], [np.nan, np.nan]], [[0, 0], [3, 2]], [[5.0, 100.0], [5.0, 100.0]])
    pairs, excluded = build_pairs(model, stations, metars, VerifyConfig())
    assert excluded["undecodable"] == 1 and excluded["no_report_within_tolerance"] == 0
    by = {(p.icao, p.step): p for p in pairs}
    assert set(by) == {("AAAA", 0), ("AAAA", 30), ("BBBB", 0)}
    assert by[("AAAA", 0)].ceiling_ft == pytest.approx(120 / 0.3048) and by[("BBBB", 0)].dz_m == 800.0
    report = verify_run(pairs, excluded, VerifyConfig(), stations_total=2)
    below500 = report["events"]["ceiling_below_500ft"]["total"]
    assert (below500["a"], below500["b"], below500["c"], below500["d"]) == (1, 0, 0, 1)  # BBBB excluded (|dz| > 300 m)
    assert report["exclusions"]["elevation_mismatch"] == 1
    conv = report["events"]["convective"]["total"]
    assert (conv["a"], conv["b"], conv["c"], conv["d"]) == (1, 0, 1, 1)  # AAAA+30 h hit, BBBB TCU missed, AAAA 0 h correct
    leads = {b["lead"]: b for b in report["events"]["convective"]["by_lead"]}
    assert leads["0-24 h"]["n"] == 2 and leads["24-48 h"]["n"] == 1 and leads["48-72 h"]["n"] == 0
    err = report["ceiling_base_error_ft"]
    assert err["n"] == 1 and err["mean_error"] == pytest.approx(120 / 0.3048 - 400)


@pytest.fixture(scope="module")
def fixture_cube(tmp_path_factory: pytest.TempPathFactory) -> xr.Dataset:
    root = tmp_path_factory.mktemp("verify")
    ingest_run(RUN, [DOMAIN], load_profile(DEFAULT_OPERATIONAL_PROFILE_PATH), FixtureFetcher(), root, [0, 3])
    run_dir = root / "fixture" / "2026092500"
    ds = xr.open_dataset(run_dir / "cube.nc")
    ds.attrs["manifest"] = (run_dir / "manifest.json").read_text()
    return ds


def test_real_daag_metars_against_the_ifs_fixture(fixture_cube: xr.Dataset) -> None:
    manifest = json.loads(fixture_cube.attrs["manifest"])
    stations = [{"icao": "DAAG", "name": "Alger", "lat": 36.691, "lon": 3.215, "elev_m": 18.0}]
    metars = [r for r in (AwcClient._metar(x) for x in DAAG_METARS) if r]
    model = model_at_stations(fixture_cube, manifest, stations, DOMAIN)
    pairs, excluded = build_pairs(model, stations, metars, VerifyConfig())
    assert [p.step for p in pairs] == [0, 3]
    i = int(np.abs(fixture_cube["lat"].values - 36.691).argmin())
    j = int(np.abs(fixture_cube["lon"].values - 3.215).argmin())
    for p in pairs:
        si = manifest["steps"].index(p.step)
        expected = float(fixture_cube["ceiling_m"].isel(step=si, lat=i, lon=j))
        assert (p.ceiling_ft is None and np.isnan(expected)) or p.ceiling_ft == pytest.approx(expected / 0.3048)
        assert p.model_convective == (float(fixture_cube["convective_class"].isel(step=si, lat=i, lon=j)) >= 2)
        assert abs((p.obs_time - p.valid_time).total_seconds()) <= 1800
        assert p.obs.station == "DAAG"
    report = verify_run(pairs, excluded, VerifyConfig(), stations_total=1)
    assert report["events"]["convective"]["total"]["n"] == 2
    assert report["parameters"]["tolerance_min"] == 30 and report["parameters"]["max_elevation_diff_m"] == 300.0


def test_valid_times_after_the_last_observation_are_not_counted_as_missing_reports() -> None:
    stations = [{"icao": "AAAA", "name": "A", "lat": 36.0, "lon": 3.0, "elev_m": 10.0},
                {"icao": "BBBB", "name": "B", "lat": 36.0, "lon": 3.25, "elev_m": 10.0}]
    metars = [{"icao": "AAAA", "obs_time": "2026-09-25T00:00:00Z", "kind": "METAR",
               "raw": "METAR AAAA 250000Z 00000KT CAVOK 15/14 Q1015"}]
    model = _model([[np.nan, np.nan], [np.nan, np.nan]], [[0, 0], [0, 0]], [[5.0, 5.0], [5.0, 5.0]])
    _, excluded = build_pairs(model, stations, metars, VerifyConfig())
    # step 0: BBBB did not report; step 30 (26/06Z) lies after the last archived observation for both
    assert excluded["no_report_within_tolerance"] == 1 and excluded["not_yet_observed"] == 2


def test_extra_fields_are_read_at_the_station_cells_and_pairs_keep_their_indices(fixture_cube: xr.Dataset) -> None:
    manifest = json.loads(fixture_cube.attrs["manifest"])
    stations = [{"icao": "DAAG", "name": "Alger", "lat": 36.691, "lon": 3.215, "elev_m": 18.0}]
    model = model_at_stations(fixture_cube, manifest, stations, DOMAIN, extra_fields=("mucape", "column_condensate"))
    i = int(np.abs(fixture_cube["lat"].values - 36.691).argmin())
    j = int(np.abs(fixture_cube["lon"].values - 3.215).argmin())
    np.testing.assert_allclose(model.extra["mucape"][:, 0], fixture_cube["mucape"].isel(lat=i, lon=j).values)
    metars = [r for r in (AwcClient._metar(x) for x in DAAG_METARS) if r]
    pairs, _ = build_pairs(model, stations, metars, VerifyConfig())
    assert [(p.k, p.n) for p in pairs] == [(0, 0), (1, 0)]
