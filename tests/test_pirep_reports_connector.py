"""
Tests for acf.connectors.pirep_reports.PIREPConnector - the real public
NOAA aviationweather.gov PIREP client backing the ESOC Earth Monitoring
panel's "Aircraft Reports (PIREP)" feed (2026-09-06, Phase 64).

Honest scope note: PIREP (pilot reports) is a real, different program
from AMDAR (automated aircraft telemetry, restricted WMO GTS, no free
public feed found) - this connector was built after confirming no real
AMDAR feed exists, and the panel row it feeds is renamed accordingly
rather than mislabeled as AMDAR.

Network access is mocked (patching requests.get) - same convention as
tests/test_argo_floats_connector.py.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import requests

from acf.connectors.pirep_reports import PIREPConnector


@pytest.fixture()
def connector():
    return PIREPConnector()


def _fake_response(status_code: int = 200, json_body=None, text: str = "") -> MagicMock:
    resp = MagicMock()
    resp.status_code = status_code
    resp.text = text
    if json_body is None:
        resp.json.side_effect = ValueError("no JSON body")
    else:
        resp.json.return_value = json_body
    return resp


def test_fetch_recent_reports_reports_real_data_on_a_genuine_200_list(connector):
    reports = [
        {"icaoId": "KMSC", "acType": "C172", "rawOb": "PNS UA /OV KPNS230005/TM 1345/FL025/TP C172/SK SKC/TB NEG "},
        {"icaoId": "KALB", "acType": "E55P", "rawOb": "ALB UA /OV 5B223005/TM 1344/FL023/TP E55P/SK BKN023 "},
    ]
    with patch.object(requests, "get", return_value=_fake_response(200, reports)) as mock_get:
        result = connector.fetch_recent_reports()

    assert result.is_real_data is True
    assert result.status == "FETCHED_OK"
    assert result.report_count == 2
    assert result.reports == reports
    assert mock_get.call_args.kwargs["params"]["bbox"]


def test_fetch_recent_reports_is_honest_on_a_network_error(connector):
    with patch.object(requests, "get", side_effect=requests.exceptions.ConnectionError("no route to host")):
        result = connector.fetch_recent_reports()

    assert result.is_real_data is False
    assert "NOT_FETCHED_NETWORK_ERROR" in result.status
    assert result.report_count == 0
    assert result.reports == []


def test_fetch_recent_reports_is_honest_on_a_non_200_status(connector):
    with patch.object(requests, "get", return_value=_fake_response(503, text="Service Unavailable")):
        result = connector.fetch_recent_reports()

    assert result.is_real_data is False
    assert "NOT_FETCHED_HTTP_503" in result.status


def test_fetch_recent_reports_is_honest_on_malformed_json(connector):
    with patch.object(requests, "get", return_value=_fake_response(200, json_body=None)):
        result = connector.fetch_recent_reports()

    assert result.is_real_data is False
    assert "NOT_FETCHED_INVALID_JSON" in result.status


def test_fetch_recent_reports_is_honest_on_an_unexpected_response_shape(connector):
    with patch.object(requests, "get", return_value=_fake_response(200, {"not": "a list"})):
        result = connector.fetch_recent_reports()

    assert result.is_real_data is False
    assert result.status == "NOT_FETCHED_UNEXPECTED_RESPONSE_SHAPE"
