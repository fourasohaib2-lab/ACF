"""
Tests for acf.connectors.nexrad_stations.NEXRADRadarConnector - the
real public NOAA api.weather.gov radar station status client backing
the ESOC Earth Monitoring panel's "Doppler Radar (NEXRAD)" feed
(2026-09-06, Phase 60).

Network access is mocked (patching requests.get) - same convention as
tests/test_argo_floats_connector.py.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import requests

from acf.connectors.nexrad_stations import NEXRADRadarConnector


@pytest.fixture()
def connector():
    return NEXRADRadarConnector()


def _fake_response(status_code: int = 200, json_body=None) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status_code
    if json_body is None:
        resp.json.side_effect = ValueError("no JSON body")
    else:
        resp.json.return_value = json_body
    return resp


def _station_body(mode: str = "Operational", last_received: str = "2026-09-06T10:44:00+00:00") -> dict:
    return {
        "properties": {
            "rda": {"properties": {"mode": mode}},
            "latency": {"levelTwoLastReceivedTime": last_received},
        }
    }


def test_fetch_station_status_reports_real_data_when_all_stations_operational(connector):
    with patch.object(requests, "get", return_value=_fake_response(200, _station_body())):
        result = connector.fetch_station_status(station_ids=("KTLX", "KOKX"))

    assert result.is_real_data is True
    assert result.status == "FETCHED_OK"
    assert result.stations_operational == 2
    assert result.stations_total == 2
    assert all(s["operational"] for s in result.stations)


def test_fetch_station_status_counts_a_non_operational_station_honestly(connector):
    responses = [_fake_response(200, _station_body(mode="Operational")), _fake_response(200, _station_body(mode="Maintenance"))]
    with patch.object(requests, "get", side_effect=responses):
        result = connector.fetch_station_status(station_ids=("KTLX", "KOKX"))

    assert result.is_real_data is True
    assert result.stations_operational == 1
    assert result.stations_total == 2


def test_fetch_station_status_is_honest_when_no_station_is_reachable(connector):
    with patch.object(requests, "get", side_effect=requests.exceptions.ConnectionError("no route to host")):
        result = connector.fetch_station_status(station_ids=("KTLX", "KOKX"))

    assert result.is_real_data is False
    assert result.status == "NOT_FETCHED_NO_STATION_REACHABLE"
    assert result.stations_operational == 0
    assert len(result.stations) == 2
    assert all("NETWORK_ERROR" in s["error"] for s in result.stations)


def test_fetch_station_status_is_real_data_if_at_least_one_station_reachable(connector):
    responses = [
        _fake_response(200, _station_body()),
        _fake_response(503),
    ]
    with patch.object(requests, "get", side_effect=responses):
        result = connector.fetch_station_status(station_ids=("KTLX", "KOKX"))

    assert result.is_real_data is True
    assert result.stations_operational == 1
    assert result.stations_total == 2
    assert result.stations[1]["error"] == "HTTP_503"


def test_fetch_station_status_is_honest_on_malformed_json(connector):
    with patch.object(requests, "get", return_value=_fake_response(200, json_body=None)):
        result = connector.fetch_station_status(station_ids=("KTLX",))

    assert result.is_real_data is False
    assert result.stations[0]["error"].startswith("INVALID_JSON")
