"""
Tests for acf.connectors.argo_floats.ArgoFloatsConnector - the real
public Argovis API client backing the ESOC Earth Monitoring panel's
"ARGO Ocean Floats" feed (2026-09-06, Phase 58).

Network access is mocked (patching requests.get) - same convention as
tests/test_eumetsat_mtg_connector.py. This project's own test suite
must not depend on live external network access.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
import requests

from acf.connectors.argo_floats import ArgoFloatsConnector


@pytest.fixture()
def connector():
    return ArgoFloatsConnector()


def _fake_response(status_code: int = 200, json_body=None, text: str = "") -> MagicMock:
    resp = MagicMock()
    resp.status_code = status_code
    resp.text = text
    if json_body is None:
        resp.json.side_effect = ValueError("no JSON body")
    else:
        resp.json.return_value = json_body
    return resp


def test_fetch_recent_profiles_reports_real_data_on_a_genuine_200_list(connector):
    profiles = [
        {"_id": "6900889_262", "geolocation": {"type": "Point", "coordinates": [-25.5677, 9.7606]}},
        {"_id": "6900889_261", "geolocation": {"type": "Point", "coordinates": [-25.6144, 9.8095]}},
    ]
    with patch.object(requests, "get", return_value=_fake_response(200, profiles)) as mock_get:
        result = connector.fetch_recent_profiles(hours_back=48.0)

    assert result.is_real_data is True
    assert result.status == "FETCHED_OK"
    assert result.profile_count == 2
    assert result.profiles == profiles
    # Real query params sent - a genuine time window, not a fabricated one.
    assert mock_get.call_args.kwargs["params"]["startDate"]
    assert mock_get.call_args.kwargs["params"]["endDate"]


def test_fetch_recent_profiles_encodes_a_real_bbox_as_a_polygon(connector):
    with patch.object(requests, "get", return_value=_fake_response(200, [])) as mock_get:
        connector.fetch_recent_profiles(bbox=(-30.0, 30.0, -20.0, 40.0))

    polygon = mock_get.call_args.kwargs["params"]["polygon"]
    coords = json.loads(polygon)
    assert coords[0] == [-30.0, 30.0]
    assert coords[2] == [-20.0, 40.0]


def test_fetch_recent_profiles_is_honest_on_a_network_error(connector):
    with patch.object(requests, "get", side_effect=requests.exceptions.ConnectionError("no route to host")):
        result = connector.fetch_recent_profiles()

    assert result.is_real_data is False
    assert "NOT_FETCHED_NETWORK_ERROR" in result.status
    assert result.profile_count == 0
    assert result.profiles == []


def test_fetch_recent_profiles_is_honest_on_a_non_200_status(connector):
    with patch.object(requests, "get", return_value=_fake_response(503, text="Service Unavailable")):
        result = connector.fetch_recent_profiles()

    assert result.is_real_data is False
    assert "NOT_FETCHED_HTTP_503" in result.status


def test_fetch_recent_profiles_is_honest_on_malformed_json(connector):
    with patch.object(requests, "get", return_value=_fake_response(200, json_body=None)):
        result = connector.fetch_recent_profiles()

    assert result.is_real_data is False
    assert "NOT_FETCHED_INVALID_JSON" in result.status


def test_fetch_recent_profiles_is_honest_on_an_unexpected_response_shape(connector):
    with patch.object(requests, "get", return_value=_fake_response(200, {"not": "a list"})):
        result = connector.fetch_recent_profiles()

    assert result.is_real_data is False
    assert result.status == "NOT_FETCHED_UNEXPECTED_RESPONSE_SHAPE"
