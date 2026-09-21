"""Tests for the new AWCI Observation Hub (src/awci/observations/hub.py),
built while working through the full remaining-gaps list ("On les
attaque toutes un par un") after it was identified as the specific,
named gap in docs/architecture/acf_awci_architecture_gap_analysis.md
("awci/observations/ ... no single observations/hub.py aggregation
point").

ObservationsHub is a pure delegation/aggregation class - it computes
nothing of its own, only calls each already-real, already-tested
connector (awci.knowledge.icao.live_source, awci.data.connectors.
pirep_reports/nexrad_stations/eumetsat_mtg) and assembles their real
results. These tests verify the DELEGATION/WIRING this module actually
adds (correct arguments passed through, correct field assembly), using
the same real dataclass shapes those connectors already define - not
re-testing their own already-covered real network/parsing behavior
(see tests/test_aviation_live_source.py, tests/
test_eumetsat_mtg_connector.py, etc. for that).
"""

from __future__ import annotations

import time

from awci.data.connectors.eumetsat_mtg import MTGFetchResult
from awci.data.connectors.nexrad_stations import NexradFetchResult
from awci.data.connectors.pirep_reports import PIREPFetchResult
from awci.knowledge.icao.live_source import LiveReport, LiveStationBundle
from awci.observations import ObservationsHub, ObservationsSnapshot


class _FakePirepConnector:
    def __init__(self, result: PIREPFetchResult) -> None:
        self._result = result
        self.calls: list[str] = []

    def fetch_recent_reports(self, bbox: str) -> PIREPFetchResult:
        self.calls.append(bbox)
        return self._result


class _FakeRadarConnector:
    def __init__(self, result: NexradFetchResult) -> None:
        self._result = result
        self.calls: list[tuple[str, ...]] = []

    def fetch_station_status(self, station_ids: tuple[str, ...]) -> NexradFetchResult:
        self.calls.append(station_ids)
        return self._result


class _FakeSatelliteConnector:
    def __init__(self, result: MTGFetchResult) -> None:
        self._result = result
        self.calls = 0

    def fetch_latest_image(self) -> MTGFetchResult:
        self.calls += 1
        return self._result


def _real_pirep_result() -> PIREPFetchResult:
    return PIREPFetchResult(is_real_data=True, status="OK", report_count=2, reports=[{"raw": "UA /OV KJFK"}])


def _real_radar_result() -> NexradFetchResult:
    return NexradFetchResult(is_real_data=True, status="OK", stations_operational=3, stations_total=3)


def _real_satellite_result() -> MTGFetchResult:
    return MTGFetchResult(is_real_data=True, status="OK", authenticated=False, product_id="MTI1-FCI")


def _real_station_bundle(icao_code: str) -> LiveStationBundle:
    bundle = LiveStationBundle(icao_code=icao_code)
    bundle.metar.raw_text = f"{icao_code} 211200Z 27010KT CAVOK 15/08 Q1013"
    return bundle


def _build_hub(pirep=None, radar=None, satellite=None) -> tuple[ObservationsHub, dict]:
    fakes = {
        "pirep": pirep or _FakePirepConnector(_real_pirep_result()),
        "radar": radar or _FakeRadarConnector(_real_radar_result()),
        "satellite": satellite or _FakeSatelliteConnector(_real_satellite_result()),
    }
    hub = ObservationsHub(
        pirep_connector=fakes["pirep"],
        radar_connector=fakes["radar"],
        satellite_connector=fakes["satellite"],
    )
    return hub, fakes


# --------------------------------------------------------------------- construction


def test_hub_constructs_real_default_connectors_when_none_supplied():
    from awci.data.connectors.eumetsat_mtg import EUMETSATMTGConnector
    from awci.data.connectors.nexrad_stations import NEXRADRadarConnector
    from awci.data.connectors.pirep_reports import PIREPConnector

    hub = ObservationsHub()
    assert isinstance(hub.pirep_connector, PIREPConnector)
    assert isinstance(hub.radar_connector, NEXRADRadarConnector)
    assert isinstance(hub.satellite_connector, EUMETSATMTGConnector)


def test_hub_accepts_injected_connectors():
    hub, fakes = _build_hub()
    assert hub.pirep_connector is fakes["pirep"]
    assert hub.radar_connector is fakes["radar"]
    assert hub.satellite_connector is fakes["satellite"]


# --------------------------------------------------------------------- individual fetch delegation


def test_fetch_pireps_delegates_with_the_real_bbox_and_returns_the_real_result():
    fake_pirep = _FakePirepConnector(_real_pirep_result())
    hub, _ = _build_hub(pirep=fake_pirep)
    result = hub.fetch_pireps(bbox="10,-100,50,-60")
    assert fake_pirep.calls == ["10,-100,50,-60"]
    assert result is fake_pirep._result
    assert result.is_real_data is True


def test_fetch_pireps_uses_the_real_default_bbox_when_not_supplied():
    from awci.data.connectors.pirep_reports import DEFAULT_BBOX

    fake_pirep = _FakePirepConnector(_real_pirep_result())
    hub, _ = _build_hub(pirep=fake_pirep)
    hub.fetch_pireps()
    assert fake_pirep.calls == [DEFAULT_BBOX]


def test_fetch_radar_status_delegates_with_the_real_station_ids():
    fake_radar = _FakeRadarConnector(_real_radar_result())
    hub, _ = _build_hub(radar=fake_radar)
    result = hub.fetch_radar_status(station_ids=("KTLX",))
    assert fake_radar.calls == [("KTLX",)]
    assert result.stations_operational == 3


def test_fetch_satellite_image_delegates_and_returns_the_real_result():
    fake_satellite = _FakeSatelliteConnector(_real_satellite_result())
    hub, _ = _build_hub(satellite=fake_satellite)
    result = hub.fetch_satellite_image()
    assert fake_satellite.calls == 1
    assert result.product_id == "MTI1-FCI"


def test_fetch_station_delegates_to_the_real_live_source_function(monkeypatch):
    import awci.observations.hub as hub_module

    expected = _real_station_bundle("LFPG")
    calls: list[tuple[str, float]] = []

    def fake_fetch(icao_code, timeout=8.0):
        calls.append((icao_code, timeout))
        return expected

    monkeypatch.setattr(hub_module, "fetch_and_decode_station", fake_fetch)
    hub, _ = _build_hub()
    result = hub.fetch_station("LFPG", timeout=5.0)
    assert calls == [("LFPG", 5.0)]
    assert result is expected


def test_fetch_sigmets_delegates_to_the_real_live_source_function(monkeypatch):
    import awci.observations.hub as hub_module

    expected = [LiveReport(raw_text="WSFR31 LFPW 211200")]
    calls: list[float] = []

    def fake_fetch(timeout=8.0):
        calls.append(timeout)
        return expected

    monkeypatch.setattr(hub_module, "fetch_active_sigmets", fake_fetch)
    hub, _ = _build_hub()
    result = hub.fetch_sigmets(timeout=3.0)
    assert calls == [3.0]
    assert result is expected


# --------------------------------------------------------------------- fetch_all aggregation


def test_fetch_all_assembles_every_real_source_into_one_snapshot(monkeypatch):
    import awci.observations.hub as hub_module

    station_bundle = _real_station_bundle("EGLL")
    sigmets = [LiveReport(raw_text="WSFR31 LFPW 211200")]
    monkeypatch.setattr(hub_module, "fetch_and_decode_station", lambda icao_code, timeout=8.0: station_bundle)
    monkeypatch.setattr(hub_module, "fetch_active_sigmets", lambda timeout=8.0: sigmets)

    pirep_result = _real_pirep_result()
    radar_result = _real_radar_result()
    satellite_result = _real_satellite_result()
    hub, _ = _build_hub(
        pirep=_FakePirepConnector(pirep_result),
        radar=_FakeRadarConnector(radar_result),
        satellite=_FakeSatelliteConnector(satellite_result),
    )

    before = time.time()
    snapshot = hub.fetch_all("EGLL")
    after = time.time()

    assert isinstance(snapshot, ObservationsSnapshot)
    assert snapshot.icao_code == "EGLL"
    assert snapshot.station is station_bundle
    assert snapshot.sigmets is sigmets
    assert snapshot.pireps is pirep_result
    assert snapshot.radar is radar_result
    assert snapshot.satellite is satellite_result
    assert before <= snapshot.fetched_at <= after


def test_fetch_all_never_fabricates_an_aggregate_verdict(monkeypatch):
    """Discipline check: ObservationsSnapshot carries no synthesized
    overall 'all good' field - only the real, unmodified per-source
    results, each with its own honest is_real_data/status."""
    import awci.observations.hub as hub_module

    monkeypatch.setattr(hub_module, "fetch_and_decode_station", lambda icao_code, timeout=8.0: _real_station_bundle(icao_code))
    monkeypatch.setattr(hub_module, "fetch_active_sigmets", lambda timeout=8.0: [])
    hub, _ = _build_hub()
    snapshot = hub.fetch_all("KJFK")
    field_names = set(ObservationsSnapshot.__dataclass_fields__)
    assert "status" not in field_names
    assert "overall_status" not in field_names
    assert "is_real_data" not in field_names
    assert snapshot.pireps.is_real_data is True  # the real per-source field, preserved


def test_fetch_all_preserves_a_real_dishonest_source_failure(monkeypatch):
    """When one real source genuinely failed (is_real_data=False), the
    hub must surface that unchanged, never silently upgrading it."""
    import awci.observations.hub as hub_module

    monkeypatch.setattr(hub_module, "fetch_and_decode_station", lambda icao_code, timeout=8.0: _real_station_bundle(icao_code))
    monkeypatch.setattr(hub_module, "fetch_active_sigmets", lambda timeout=8.0: [])
    failed_pirep = PIREPFetchResult(is_real_data=False, status="NOT_FETCHED_NETWORK_ERROR: timeout")
    hub, _ = _build_hub(pirep=_FakePirepConnector(failed_pirep))
    snapshot = hub.fetch_all("KJFK")
    assert snapshot.pireps.is_real_data is False
    assert "NOT_FETCHED_NETWORK_ERROR" in snapshot.pireps.status


# --------------------------------------------------------------------- discipline


def test_hub_does_not_reimplement_the_argo_or_live_connectors_registry():
    """Confirms the disclosed exclusions in hub.py's own docstring:
    no real usage of Argo floats (ocean, not aviation) or the still-
    disclosed-unconnected LiveDataConnectorEngine registry - checking
    actual imports, not the docstring text that names them as
    deliberately excluded."""
    import awci.observations.hub as hub_module

    assert not hasattr(hub_module, "ArgoFloatsConnector")
    assert not hasattr(hub_module, "LiveDataConnectorEngine")
