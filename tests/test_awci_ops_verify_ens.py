"""ENS probabilistic verification: Brier, fair Brier, Murphy decomposition, pairs, real DAAG case on the fixtures."""

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import numpy as np
import pytest

from acf.awci.obs.source_awc import AwcClient
from acf.awci.ops.engine import DEFAULT_OPERATIONAL_PROFILE_PATH, load_profile
from acf.awci.ops.ens_ingest import ingest_ens_run
from acf.awci.ops.ens_store import EnsStore
from acf.awci.ops.ingest import ingest_run
from acf.awci.ops.store import CubeStore
from acf.awci.ops.verify import ModelAtStations, VerifyConfig, build_pairs, model_at_stations
from acf.awci.ops.verify_ens import (
    EnsAtStations,
    ProbabilisticSample,
    brier_scores,
    ens_at_stations,
    ens_samples,
    verify_ens_run,
)
from tests.awci_ops_support import DOMAIN, ENS_FIXTURE, FixtureFetcher

RUN = datetime(2026, 9, 25, 0, tzinfo=UTC)
DAAG_METARS = json.loads((Path(__file__).parent / "data" / "awc" / "metar_daag_20260925.json").read_text())


def _s(count: int, observed: bool, det: bool, members: int = 50, step: int = 0) -> ProbabilisticSample:
    return ProbabilisticSample("convective", step, count, members, observed, det)


def test_brier_scores_on_hand_computed_cases() -> None:
    # p = 0.5, 0, 1, 0.2 against o = 1, 0, 1, 0; deterministic 1, 0, 0, 1
    s = brier_scores([_s(25, True, True), _s(0, False, False), _s(50, True, False), _s(10, False, True)])
    assert s["n"] == 4 and s["observed_events"] == 2 and s["observed_frequency"] == 0.5
    assert s["brier"] == pytest.approx((0.25 + 0 + 0 + 0.04) / 4)
    # Ferro (2014): minus p(1-p)/(m-1) per case
    assert s["fair_brier"] == pytest.approx((0.29 - (0.25 + 0.16) / 49) / 4)
    assert s["uncertainty"] == 0.25 and s["bss_climatology"] == pytest.approx(1 - 0.0725 / 0.25)
    assert s["brier_deterministic"] == 0.5 and s["skill_vs_deterministic"] == pytest.approx(1 - 0.0725 / 0.5)
    # one case per bin: REL = BS, RES = UNC, the decomposition is exact
    assert s["reliability"] == pytest.approx(0.0725) and s["resolution"] == pytest.approx(0.25)
    assert s["decomposition_residual"] == pytest.approx(0.0, abs=1e-12)
    bins = {b["lower"]: b for b in s["diagram"] if b["n"]}
    assert set(bins) == {0.0, 0.2, 0.5, 0.9}  # p = 1 falls in the last, closed bin; p = 0.2 in [0.2, 0.3)
    assert bins[0.9]["mean_forecast"] == 1.0 and bins[0.9]["observed_frequency"] == 1.0
    assert s["sufficient"] is False  # 2 observed events < 10


def test_decomposition_residual_is_reported_when_bins_hold_several_probabilities() -> None:
    s = brier_scores([_s(1, False, False), _s(4, True, False)])  # p = 0.02 and 0.08 share the bin [0, 0.1)
    assert s["decomposition_residual"] != pytest.approx(0.0, abs=1e-6)
    assert s["brier"] == pytest.approx(s["reliability"] - s["resolution"] + s["uncertainty"]
                                       + s["decomposition_residual"])


def test_undefined_scores_are_null() -> None:
    empty = brier_scores([])
    assert empty["n"] == 0 and empty["brier"] is None and empty["sufficient"] is False
    never = brier_scores([_s(0, False, False), _s(5, False, False)])  # no event observed nor forecast by det
    assert never["uncertainty"] == 0 and never["bss_climatology"] is None and never["skill_vs_deterministic"] is None
    single = brier_scores([_s(1, True, True, members=1)])
    assert single["fair_brier"] is None  # undefined for a one-member ensemble


def _model() -> ModelAtStations:
    t0 = datetime(2026, 9, 25, 0, tzinfo=UTC)
    return ModelAtStations(steps=[0, 3, 6], valid_times=[t0 + timedelta(hours=h) for h in (0, 3, 6)],
                           missing_steps=[], icao=["AAAA", "BBBB"], grid_lat=[36.0, 36.0], grid_lon=[3.0, 3.25],
                           ceiling_m=np.array([[120.0, 120.0], [np.nan, np.nan], [np.nan, 300.0]]),
                           convective_class=np.array([[0, 0], [0, 0], [3, 0]]),
                           surface_height_m=np.array([[5.0, 100.0]] * 3))


def test_samples_follow_the_deterministic_pairs_on_ens_steps_only() -> None:
    stations = [{"icao": "AAAA", "name": "A", "lat": 36.0, "lon": 3.0, "elev_m": 10.0},
                {"icao": "BBBB", "name": "B", "lat": 36.0, "lon": 3.25, "elev_m": 900.0}]
    raw = {("AAAA", 0): "2000 BR BKN004 15/14", ("AAAA", 3): "CAVOK 15/14", ("AAAA", 6): "9999 FEW030CB 25/14",
           ("BBBB", 0): "9999 SCT030TCU 15/10", ("BBBB", 6): "AUTO 9999 NCD 20/10"}
    metars = [{"icao": icao, "obs_time": f"2026-09-25T{h:02d}:00:00Z", "kind": "METAR",
               "raw": f"METAR {icao} 25{h:02d}00Z 00000KT {tail} Q1015"} for (icao, h), tail in raw.items()]
    pairs, _ = build_pairs(_model(), stations, metars, VerifyConfig())
    ens = EnsAtStations(steps=[0, 6], missing_steps=[],
                        count={"p_ceiling_1500ft": np.array([[40, 3], [0, 0]]), "p_convection": np.array([[2, 10], [30, 0]])},
                        members={"p_ceiling_1500ft": np.array([[50, 50], [50, 50]]),
                                 "p_convection": np.array([[50, 50], [50, 0]])})
    samples, excl = ens_samples(pairs, ens, VerifyConfig())
    assert excl["not_an_ens_step"] == 1  # AAAA +3 h
    assert excl["elevation_mismatch"] == 2  # BBBB (|dz| = 800 m) at 0 and 6 h: no ceiling case
    assert excl["convection_unknown"] == 1  # BBBB +6 h: AUTO NCD cannot exclude convection
    got = {(s.event, s.step, s.count, s.members, s.observed, s.deterministic) for s in samples}
    assert got == {("ceiling_below_1500ft", 0, 40, 50, True, True), ("convective", 0, 2, 50, False, False),
                   ("convective", 0, 10, 50, True, False), ("ceiling_below_1500ft", 6, 0, 50, False, False),
                   ("convective", 6, 30, 50, True, True)}


def test_no_member_is_excluded_not_counted_as_zero() -> None:
    stations = [{"icao": "AAAA", "name": "A", "lat": 36.0, "lon": 3.0, "elev_m": 10.0}]
    metars = [{"icao": "AAAA", "obs_time": "2026-09-25T00:00:00Z", "kind": "METAR",
               "raw": "METAR AAAA 250000Z 00000KT CAVOK 15/14 Q1015"}]
    pairs, _ = build_pairs(_model(), stations, metars, VerifyConfig())
    ens = EnsAtStations(steps=[0], missing_steps=[], count={"p_ceiling_1500ft": np.zeros((1, 2), int),
                                                           "p_convection": np.zeros((1, 2), int)},
                        members={"p_ceiling_1500ft": np.array([[50, 50]]), "p_convection": np.array([[0, 0]])})
    samples, excl = ens_samples(pairs, ens, VerifyConfig())
    assert [s.event for s in samples] == ["ceiling_below_1500ft"] and excl["no_ens_member"] == 1


def test_report_flags_a_cloud_profile_mismatch() -> None:
    report = verify_ens_run([_s(25, True, True)], {}, VerifyConfig(), {"ens": "1.2.0", "deterministic": "1.1.0"})
    assert report["like_for_like"] is False and report["events"]["convective"]["total"]["n"] == 1
    assert report["events"]["ceiling_below_1500ft"]["total"]["n"] == 0
    assert [b["step"] for b in report["events"]["convective"]["by_step"]] == [0]


@pytest.fixture(scope="module")
def cubes(tmp_path_factory: pytest.TempPathFactory) -> Path:
    root = tmp_path_factory.mktemp("verify_ens")
    ingest_run(RUN, [DOMAIN], load_profile(DEFAULT_OPERATIONAL_PROFILE_PATH), FixtureFetcher(), root, [0, 3])
    ingest_ens_run(RUN, DOMAIN, FixtureFetcher(root=ENS_FIXTURE), root, steps=[0, 6], members=[1, 2, 3, 4])
    return root


def test_real_daag_metars_against_the_ens_fixture(cubes: Path) -> None:
    det, ens_store = CubeStore(cubes), EnsStore(cubes)
    manifest, ds = det.manifest("fixture", "2026092500"), det.dataset("fixture", "2026092500")
    ens_manifest, ens_ds = ens_store.manifest("fixture", "2026092500"), ens_store.dataset("fixture", "2026092500")
    stations = [{"icao": "DAAG", "name": "Alger", "lat": 36.691, "lon": 3.215, "elev_m": 18.0}]
    metars = [r for r in (AwcClient._metar(x) for x in DAAG_METARS) if r]
    model = model_at_stations(ds, manifest, stations, DOMAIN)
    pairs, _ = build_pairs(model, stations, metars, VerifyConfig())
    ens = ens_at_stations(ens_ds, ens_manifest, model, ds["lat"].values, ds["lon"].values)
    samples, excl = ens_samples(pairs, ens, VerifyConfig())
    assert excl["not_an_ens_step"] == 1 and len(samples) >= 1  # deterministic +3 h has no ENS counterpart
    i = int(np.abs(ens_ds["lat"].values - 36.691).argmin())
    j = int(np.abs(ens_ds["lon"].values - 3.215).argmin())
    for s in samples:
        product = {"convective": "p_convection", "ceiling_below_1500ft": "p_ceiling_1500ft"}[s.event]
        assert s.step == 0 and s.members == int(ens_ds[f"{product}_n"].isel(step=0, lat=i, lon=j))
        assert s.count == int(ens_ds[f"{product}_count"].isel(step=0, lat=i, lon=j)) and 0 <= s.count <= 4


def test_grid_mismatch_is_an_error(cubes: Path) -> None:
    ens_store, det = EnsStore(cubes), CubeStore(cubes)
    ds = det.dataset("fixture", "2026092500")
    model = model_at_stations(ds, det.manifest("fixture", "2026092500"),
                              [{"icao": "DAAG", "name": "Alger", "lat": 36.691, "lon": 3.215}], DOMAIN)
    with pytest.raises(ValueError, match="same grid"):
        ens_at_stations(ens_store.dataset("fixture", "2026092500"), ens_store.manifest("fixture", "2026092500"),
                        model, ds["lat"].values[:-1], ds["lon"].values)

