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
