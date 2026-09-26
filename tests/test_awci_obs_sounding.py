"""SP7 radiosondes: IGRA station list and Wyoming CSV (real fixtures), wind convention, observed shear, client
behaviour (missing profile, failed request), ingestion, pairing on the real IFS fixture, scores, API."""

import math
import urllib.error
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from fastapi.testclient import TestClient

from acf.awci.obs.ingest import ingest_soundings, sounding_times
from acf.awci.obs.sounding import (
    SoundingError,
    UwyoClient,
    parse_igra_stations,
    parse_uwyo_csv,
    stations_in,
    wind_components,
)
from acf.awci.obs.store import ObsStore
from acf.awci.ops.domains import Domain
from acf.awci.ops.engine import DEFAULT_OPERATIONAL_PROFILE_PATH, load_profile
from acf.awci.ops.ingest import ingest_run
from acf.awci.ops.kinematics import layer_shear
from acf.awci.ops.store import CubeStore
from acf.awci.ops.verify_sounding import ColumnPair, column_pairs, verify_soundings
from acf.web.awci_app import create_awci_app
from tests.awci_ops_support import DOMAIN, FixtureFetcher

DATA = Path(__file__).parent / "data" / "awci_soundings"
IGRA = (DATA / "igra2-station-list-excerpt.txt").read_text()
ALGER_CSV = (DATA / "uwyo_60390_2026092500.csv").read_text()
NOMINAL = datetime(2026, 9, 25, 0, tzinfo=UTC)
RUN = NOMINAL
NORTH_AFRICA = Domain("north_africa", "na", 15.0, 45.0, -20.0, 40.0, True)
LEVELS = [1000, 925, 850, 700, 600, 500, 400, 300, 250, 200, 150, 100]


def _alger() -> dict[str, Any]:
    record = parse_uwyo_csv(ALGER_CSV, "60390", NOMINAL)
    assert record is not None
    return record | {"name": "DAR-EL-BEIDA", "elev_m": 25.0}


def test_igra_station_list() -> None:
    stations = parse_igra_stations(IGRA + "short line\n")
    assert [s.wmo for s in stations] == ["60360", "60390", "94203", "60155"]  # AGXUAE04843 is not a WMO id
    alger = stations[1]
    assert (alger.igra_id, alger.name, alger.lat, alger.lon, alger.elev_m, alger.last_year) == (
        "AGM00060390", "DAR-EL-BEIDA", 36.6899, 3.2166, 25.0, 2026)
    assert [s.wmo for s in stations_in(stations, NORTH_AFRICA, 2026)] == ["60390", "60155"]  # Annaba ended 2008
    assert [s.wmo for s in stations_in(stations, DOMAIN, 2026)] == ["60390"]


def test_wyoming_csv_keeps_the_awci_levels_exactly() -> None:
    record = _alger()
    assert record["nominal_time"] == "2026-09-25T00:00:00Z" and record["launch_time"] == "2026-09-24T23:31:00Z"
    assert (record["lat"], record["lon"]) == (36.68, 3.21)
    assert [lv["p_hpa"] for lv in record["levels"]] == LEVELS
    by_p = {lv["p_hpa"]: lv for lv in record["levels"]}
    line = next(r for r in ALGER_CSV.splitlines() if r.split(",")[3].strip() == "500.0").split(",")
    assert by_p[500.0]["z_m"] == float(line[4]) and by_p[500.0]["t_c"] == float(line[5])
    assert by_p[500.0]["rh_pct"] == float(line[8]) and by_p[500.0]["wspd_ms"] == float(line[12])


def test_wyoming_answers_without_a_profile() -> None:
    assert parse_uwyo_csv("", "60390", NOMINAL) is None
    assert parse_uwyo_csv("<html>Can't get 60390 ALGER</html>", "60390", NOMINAL) is None
    header = ALGER_CSV.splitlines()[0]
    assert parse_uwyo_csv(header + "\n", "60390", NOMINAL) is None


def test_wind_components_meteorological_convention() -> None:
    u, v = wind_components(10.0, 270.0)  # westerly: blows towards the east
    assert u == pytest.approx(10.0) and v == pytest.approx(0.0, abs=1e-12)
    u, v = wind_components(10.0, 0.0)  # northerly: blows towards the south
    assert u == pytest.approx(0.0, abs=1e-12) and v == pytest.approx(-10.0)
    u, v = wind_components(5.0, 135.0)
    assert math.hypot(u, v) == pytest.approx(5.0) and u < 0 < v


def test_observed_shear_is_the_model_definition(tmp_path: Path) -> None:
    pair = _pairs(tmp_path)[0][0]
    obs = pair.obs
    record = _alger()
    z = np.array([lv["z_m"] for lv in record["levels"]], dtype=float)
    _, expected = layer_shear(obs["u"][:, None], obs["v"][:, None], z[:, None])
    np.testing.assert_allclose(obs["vws"], expected[:, 0])
    np.testing.assert_allclose(obs["wind_speed"], np.hypot(obs["u"], obs["v"]), rtol=1e-12)


def _http_error(code: int) -> urllib.error.HTTPError:
    return urllib.error.HTTPError("https://weather.uwyo.edu/x", code, "Data Not Found", {}, None)  # type: ignore[arg-type]


def test_a_404_means_no_sounding(monkeypatch: pytest.MonkeyPatch) -> None:
    def not_found(request: Any, timeout: float) -> Any:
        raise _http_error(404)

    monkeypatch.setattr("urllib.request.urlopen", not_found)
    assert UwyoClient._http_get("https://weather.uwyo.edu/x") == ""

    def server_error(request: Any, timeout: float) -> Any:
        raise _http_error(503)

    monkeypatch.setattr("urllib.request.urlopen", server_error)
    with pytest.raises(SoundingError, match="503"):
        UwyoClient._http_get("https://weather.uwyo.edu/x")


def test_client_skips_missing_and_failed_requests() -> None:
    stations = stations_in(parse_igra_stations(IGRA), NORTH_AFRICA, 2026)
    urls: list[str] = []
    pauses: list[float] = []

    def get(url: str) -> str:
        urls.append(url)
        if "id=60390" in url:
            return ALGER_CSV
        raise SoundingError(f"{url}: timed out")

    client = UwyoClient(get=get, pause_s=1.5, sleep=pauses.append)
    records = client.soundings(stations, [NOMINAL])
    assert [r["wmo"] for r in records] == ["60390"] and records[0]["name"] == "DAR-EL-BEIDA"
    assert "datetime=2026-09-25+00%3A00%3A00" in urls[0] and pauses == [1.5]
    assert len(client.errors) == 1 and client.missing == []

    empty = UwyoClient(get=lambda url: "", sleep=lambda s: None)
    assert empty.soundings(stations, [NOMINAL]) == [] and empty.missing == ["60390@2026092500", "60155@2026092500"]
    down = UwyoClient(get=get, sleep=lambda s: None)
    with pytest.raises(SoundingError, match="all 1 requests failed"):
        down.soundings(stations[1:], [NOMINAL])


def test_sounding_times() -> None:
    now = datetime(2026, 9, 26, 13, 30, tzinfo=UTC)
    assert [f"{t:%d%H}" for t in sounding_times(now, 48)] == ["2500", "2512", "2600"]  # 12Z not yet published
    assert [f"{t:%d%H}" for t in sounding_times(now.replace(hour=14), 24)] == ["2600", "2612"]


def test_ingestion_caches_the_station_list_for_a_week(tmp_path: Path) -> None:
    store = ObsStore(tmp_path, DOMAIN.name)
    lists: list[int] = []

    def station_list() -> str:
        lists.append(1)
        return IGRA

    client = UwyoClient(get=lambda url: ALGER_CSV if "2026-09-25+00" in url else "", sleep=lambda s: None)
    now = datetime(2026, 9, 25, 14, tzinfo=UTC)
    result = ingest_soundings(client, store, DOMAIN, 24, now, station_list)
    assert result["soundings_added"] == 1 and result["stations"] == 1 and result["missing"] == 1
    assert ingest_soundings(client, store, DOMAIN, 24, now, station_list)["soundings_added"] == 0  # deduplicated
    assert lists == [1]
    (stored,) = store.soundings(NOMINAL, NOMINAL)
    assert stored["wmo"] == "60390" and len(stored["levels"]) == 12
    with pytest.raises(SoundingError, match="station list"):
        ingest_soundings(client, ObsStore(tmp_path / "x", DOMAIN.name), DOMAIN, 24, now, lambda: "<html></html>")


def _pairs(tmp_path: Path) -> tuple[list[ColumnPair], dict[str, int], list[float]]:
    ingest_run(RUN, [DOMAIN], load_profile(DEFAULT_OPERATIONAL_PROFILE_PATH), FixtureFetcher(), tmp_path, [0, 3])
    cubes = CubeStore(tmp_path)
    manifest = cubes.manifest(DOMAIN.name, "2026092500")
    late = _alger() | {"nominal_time": "2026-09-25T12:00:00Z"}
    away = _alger() | {"wmo": "60155", "lat": 33.57, "lon": -7.67}
    pairs, excluded = column_pairs(cubes.dataset(DOMAIN.name, "2026092500"), manifest, [_alger(), late, away], DOMAIN)
    return pairs, excluded, manifest["levels_hpa"]


def test_pairing_on_the_real_ifs_fixture(tmp_path: Path) -> None:
    pairs, excluded, levels = _pairs(tmp_path)
    assert excluded == {"no_step_at_nominal_time": 1, "outside_domain": 1}
    (pair,) = pairs
    assert pair.step == 0 and pair.valid_time == "2026-09-25T00:00:00+00:00" and list(pair.levels_hpa) == levels
    # Analysis step against the real Algiers sounding: the IFS analysis agrees within a few kelvin aloft.
    ok = np.isfinite(pair.model["t"]) & np.isfinite(pair.obs["t"])
    assert ok.sum() >= 10 and np.nanmax(np.abs(pair.model["t"] - pair.obs["t"])[ok]) < 5.0
    assert np.all((pair.model["rh"][ok] >= 0) & (pair.model["rh"][ok] <= 100))


def _pair(model: dict[str, list[float]], obs: dict[str, list[float]]) -> ColumnPair:
    arr = lambda d: {k: np.array(v, dtype=float) for k, v in d.items()}  # noqa: E731
    return ColumnPair("1", "s", 0, "t", np.array([850.0, 500.0]), arr(model), arr(obs))


def test_scores_computed_by_hand() -> None:
    base = {"rh": [50, 50], "wind_speed": [5, 5], "vws": [0.01, 0.01], "icing": [0, 1]}
    a = _pair(base | {"t": [280, 250], "u": [3, 0], "v": [4, 0]}, base | {"t": [281, 252], "u": [0, 0], "v": [0, np.nan]})
    b = _pair(base | {"t": [282, np.nan], "u": [0, 0], "v": [0, 0], "icing": [1, 1]},
              base | {"t": [280, 250], "u": [0, 0], "v": [0, 0]})
    report = verify_soundings([a, b], {"outside_domain": 0}, [850.0, 500.0], min_observed_events=1)
    t850, t500 = report["levels"][0]["t"], report["levels"][1]["t"]
    assert t850 == {"n": 2, "bias": pytest.approx(0.5), "rmse": pytest.approx(math.sqrt((1 + 4) / 2))}
    assert t500 == {"n": 1, "bias": pytest.approx(-2.0), "rmse": pytest.approx(2.0)}
    assert report["total"]["t"]["n"] == 3 and report["total"]["t"]["bias"] == pytest.approx(-1 / 3)
    assert report["levels"][0]["wind_vector_rmse"] == pytest.approx(math.sqrt(25 / 2))
    assert report["levels"][1]["wind_vector_rmse"] == pytest.approx(0.0)  # the NaN v is excluded
    icing = report["total"]["icing"]  # model [0,1,1,1] vs obs [0,1,0,1]
    assert (icing["a"], icing["b"], icing["c"], icing["d"]) == (2, 1, 0, 1)
    assert report["soundings"] == 2 and report["stations"] == 1
    empty = verify_soundings([], {}, [850.0])
    assert empty["total"]["t"] == {"n": 0, "bias": None, "rmse": None} and empty["total"]["wind_vector_rmse"] is None


DOMAINS = '{"domains": [{"name": "fixture", "label": "f", "south": 35, "north": 37, "west": 2, "east": 4, "default": true}]}'


def test_api(tmp_path: Path) -> None:
    ingest_run(RUN, [DOMAIN], load_profile(DEFAULT_OPERATIONAL_PROFILE_PATH), FixtureFetcher(), tmp_path, [0, 3])
    store = ObsStore(tmp_path, DOMAIN.name)
    store.add_soundings([_alger()])
    store.write_sounding_stations([s.as_dict() for s in stations_in(parse_igra_stations(IGRA), DOMAIN, 2026)],
                                  datetime(2026, 9, 26, tzinfo=UTC))
    domains = tmp_path / "domains.json"
    domains.write_text(DOMAINS)
    client = TestClient(create_awci_app(data_dir=tmp_path, domains_file=domains))
    body = client.get("/api/v1/awci/soundings/verification", params={"domain": "fixture", "run": "2026092500"}).json()
    assert body["soundings"] == 1 and body["stations_known"] == 1 and body["model_id"] == "ifs"
    assert [lv["level_hpa"] for lv in body["levels"]] == LEVELS and body["total"]["t"]["n"] >= 10
    assert "Wyoming" in body["observed"]
    assert client.get("/api/v1/awci/soundings/verification", params={"domain": "fixture", "run": "2026092512"}).status_code == 404
    assert client.get("/api/v1/awci/soundings/verification", params={"domain": "nope", "run": "2026092500"}).status_code == 404
    assert client.get("/api/v1/awci/soundings/verification", params={"domain": "fixture", "run": "2026092500",
                                                                      "model": "gfs"}).status_code == 404
    assert client.get("/api/v1/awci/soundings/verification", params={"domain": "fixture", "run": "x"}).status_code == 422
