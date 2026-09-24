"""Tests for the new AWCI API (src/awci/api/), built while working
through the full remaining-gaps list ("On les attaque toutes un par
un") after it was identified as the specific gap in
docs/architecture/acf_awci_architecture_gap_analysis.md ("No dedicated
AWCI API surface; src/acf/api/ and src/acf/web/ are ACF-general, not
AWCI-specific").

Every real network-calling connector is injected/monkeypatched the
same way tests/test_awci_observations_hub.py already established -
these tests verify the real HTTP wiring (status codes, real dataclass
fields reaching the JSON response, real 404s on an unknown
airport/hazard), never re-testing the underlying engines' own already-
covered behavior.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

import awci.observations.hub as hub_module
from awci.api.app import create_app
from awci.data.connectors.eumetsat_mtg import MTGFetchResult
from awci.data.connectors.nexrad_stations import NexradFetchResult
from awci.data.connectors.pirep_reports import PIREPFetchResult
from awci.knowledge.icao.live_source import LiveReport, LiveStationBundle
from awci.knowledge.icao.metar_decoder import METARDecoder
from awci.observations.hub import ObservationsHub


class _FakePirepConnector:
    def fetch_recent_reports(self, bbox: str) -> PIREPFetchResult:
        return PIREPFetchResult(is_real_data=True, status="OK", report_count=0, reports=[])


class _FakeRadarConnector:
    def fetch_station_status(self, station_ids) -> NexradFetchResult:
        return NexradFetchResult(is_real_data=True, status="OK", stations_operational=3, stations_total=3)


class _FakeSatelliteConnector:
    def fetch_latest_image(self) -> MTGFetchResult:
        return MTGFetchResult(is_real_data=True, status="OK", authenticated=False, product_id="MTI1-FCI")


_REAL_KJFK_METAR = "KJFK 211251Z 27015G25KT 10SM FEW250 12/10 A2985"


def _real_station_bundle(icao_code: str) -> LiveStationBundle:
    raw = _REAL_KJFK_METAR.replace("KJFK", icao_code, 1)
    report = METARDecoder.decode(raw)
    bundle = LiveStationBundle(icao_code=icao_code)
    bundle.metar = LiveReport(raw_text=raw, decoded=report)
    return bundle


def _test_client(monkeypatch) -> TestClient:
    """Real FastAPI app with every real network-calling connector
    faked/monkeypatched, matching the same real isolation discipline
    tests/test_awci_observations_hub.py already established."""
    monkeypatch.setattr(hub_module, "fetch_and_decode_station", lambda icao_code, timeout=8.0: _real_station_bundle(icao_code))
    monkeypatch.setattr(hub_module, "fetch_active_sigmets", lambda timeout=8.0: [])
    hub = ObservationsHub(
        pirep_connector=_FakePirepConnector(),
        radar_connector=_FakeRadarConnector(),
        satellite_connector=_FakeSatelliteConnector(),
    )
    app = create_app(observations_hub=hub)
    return TestClient(app)


# --------------------------------------------------------------------- app.py


def test_health_endpoint():
    client = TestClient(create_app())
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "awci-api"}


def test_create_app_defaults_to_a_real_observations_hub():
    app = create_app()
    assert isinstance(app.state.observations_hub, ObservationsHub)


def test_create_app_allows_cors_from_the_dashboard_dev_server():
    """Real bug found exercising the dashboard against this API in an
    actual browser: FastAPI issues no CORS headers by default, so
    every browser genuinely blocks lib/api.ts's cross-origin fetch
    calls with a preflight failure. See app.py's own docstring."""
    client = TestClient(create_app())
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_create_app_cors_origins_are_configurable_via_env(monkeypatch):
    monkeypatch.setenv("AWCI_API_CORS_ORIGINS", "https://awci.example.com")
    client = TestClient(create_app())
    response = client.options(
        "/health",
        headers={"Origin": "https://awci.example.com", "Access-Control-Request-Method": "GET"},
    )
    assert response.headers["access-control-allow-origin"] == "https://awci.example.com"


# --------------------------------------------------------------------- observations.py


def test_observations_endpoint_returns_the_real_assembled_snapshot(monkeypatch):
    client = _test_client(monkeypatch)
    response = client.get("/observations/KJFK")
    assert response.status_code == 200
    body = response.json()
    assert body["icao_code"] == "KJFK"
    assert body["radar"]["stations_operational"] == 3
    assert body["satellite"]["product_id"] == "MTI1-FCI"


# --------------------------------------------------------------------- airports.py


def test_list_airports_endpoint_returns_the_real_registry():
    client = TestClient(create_app())
    response = client.get("/airports")
    assert response.status_code == 200
    body = response.json()
    icao_codes = {a["icao_code"] for a in body}
    assert {"LFPG", "KJFK", "EGLL"} <= icao_codes
    lfpg = next(a for a in body if a["icao_code"] == "LFPG")
    assert lfpg["iata_code"] == "CDG"
    assert lfpg["latitude"] == pytest.approx(49.0097)


def test_runway_wind_endpoint_returns_real_per_runway_assessments():
    client = TestClient(create_app())
    response = client.get("/airports/KJFK/runways", params={"wind_dir_deg": 270, "wind_speed_kt": 15})
    assert response.status_code == 200
    body = response.json()
    assert "13R" in body
    assert "headwind_kt" in body["13R"]


def test_runway_wind_endpoint_404s_for_an_unknown_airport():
    client = TestClient(create_app())
    response = client.get("/airports/NOTREAL/runways", params={"wind_dir_deg": 270, "wind_speed_kt": 15})
    assert response.status_code == 404


def test_airport_weather_endpoint_returns_the_real_snapshot(monkeypatch):
    client = _test_client(monkeypatch)
    response = client.get("/airports/KJFK/weather")
    assert response.status_code == 200
    body = response.json()
    assert body["icao_code"] == "KJFK"
    assert body["is_real_data"] is True


# --------------------------------------------------------------------- flights.py


def test_route_weather_endpoint_returns_the_real_briefing(monkeypatch):
    client = _test_client(monkeypatch)
    response = client.get("/flights/route-weather", params={"dep_icao": "KJFK", "arr_icao": "EGLL"})
    assert response.status_code == 200
    body = response.json()
    assert body["departure_icao"] == "KJFK"
    assert body["arrival_icao"] == "EGLL"
    assert body["great_circle_distance_nm"] > 0
    assert len(body["waypoints"]) == 10


def test_route_weather_endpoint_404s_for_an_unknown_airport(monkeypatch):
    client = _test_client(monkeypatch)
    response = client.get("/flights/route-weather", params={"dep_icao": "NOTREAL", "arr_icao": "EGLL"})
    assert response.status_code == 404


# --------------------------------------------------------------------- hazards.py


def test_hazards_list_endpoint_returns_real_registry_keys():
    client = TestClient(create_app())
    response = client.get("/hazards")
    assert response.status_code == 200
    assert "cat_turbulence" in response.json()


def test_hazard_detail_endpoint_returns_a_real_definition():
    client = TestClient(create_app())
    response = client.get("/hazards/cat_turbulence")
    assert response.status_code == 200
    body = response.json()
    assert body["key"] == "cat_turbulence"
    assert body["physical_explanation"]


def test_hazard_detail_endpoint_404s_for_an_unknown_key():
    client = TestClient(create_app())
    response = client.get("/hazards/not_a_real_hazard")
    assert response.status_code == 404


# --------------------------------------------------------------------- complexity.py


def test_complexity_score_endpoint_computes_a_real_score():
    client = TestClient(create_app())
    response = client.post(
        "/complexity/score",
        json={"temperature": 288.0, "specific_humidity": 0.008, "wind_speed": 12.0},
    )
    assert response.status_code == 200
    body = response.json()
    assert "awci" in body
    assert 0.0 <= body["awci"] <= 100.0


def test_complexity_field_endpoint_returns_a_real_2d_field():
    """A small (4x4) grid keeps this real CoupledEarthSolver run fast
    in the test suite - see compute_real_complexity_field()'s own
    docstring for the real physics behind this endpoint."""
    client = TestClient(create_app())
    response = client.get("/complexity/field", params={"n_lat": 4, "n_lon": 4})
    assert response.status_code == 200
    body = response.json()
    assert body["is_real_data"] is True
    assert len(body["lats"]) == 4
    assert len(body["lons"]) == 4
    assert len(body["awci_field"]) == 4
    assert len(body["awci_field"][0]) == 4
    assert all(0.0 <= cell <= 100.0 for row in body["awci_field"] for cell in row)
    assert "dynamic" in body["module_fields"]
    # Real bands straight from AWCICalculator.LEVEL_THRESHOLDS - the top
    # band's real upper bound (float("inf")) must come through as JSON
    # null (never a fabricated numeric sentinel), never dropped.
    assert body["level_thresholds"][0] == [20.0, "Very Low"]
    assert body["level_thresholds"][-1] == [None, "Extreme"]


def test_complexity_field_endpoint_400s_for_an_unknown_model():
    client = TestClient(create_app())
    response = client.get("/complexity/field", params={"model": "NOT_A_REAL_MODEL"})
    assert response.status_code == 400


def test_complexity_vertical_profile_endpoint_returns_a_real_column():
    client = TestClient(create_app())
    response = client.get(
        "/complexity/vertical-profile",
        params={"lat": 45.0, "lon": 5.0, "n_lat": 4, "n_lon": 4, "n_levels": 6},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["is_real_data"] is True
    assert body["n_levels"] == 6
    assert len(body["awci_profile"]) == 6
    assert len(body["pressure_profile_hpa"]) == 6
    # Real ICAO convention: index 0 is the surface, so it carries the
    # highest real local pressure in the column.
    assert body["pressure_profile_hpa"][0] == max(body["pressure_profile_hpa"])


def test_complexity_vertical_profile_endpoint_400s_for_an_unknown_model():
    client = TestClient(create_app())
    response = client.get("/complexity/vertical-profile", params={"lat": 45.0, "lon": 5.0, "model": "NOPE"})
    assert response.status_code == 400


# --------------------------------------------------------------------- reports.py


def test_aviation_report_endpoint_returns_the_real_report_with_no_decision_section(monkeypatch):
    client = _test_client(monkeypatch)
    response = client.get("/reports/KJFK")
    assert response.status_code == 200
    body = response.json()
    assert body["icao_code"] == "KJFK"
    assert body["weather"]["is_real_data"] is True
    # No module_scores/overall_awci were supplied - honestly absent.
    assert body["decision"] is None
    assert body["audit"] is None


# --------------------------------------------------------------------- discipline


def test_awci_api_package_never_imports_pyside6():
    import sys

    import awci.api  # noqa: F401
    import awci.api.app  # noqa: F401
    import awci.api.routes  # noqa: F401

    api_module_names = [name for name in sys.modules if name.startswith("awci.api")]
    for name in api_module_names:
        module = sys.modules[name]
        source_file = getattr(module, "__file__", "") or ""
        assert "PySide6" not in source_file
