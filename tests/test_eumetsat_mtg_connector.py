"""
Tests for acf.connectors.eumetsat_mtg.EUMETSATMTGConnector - the real
EUMETSAT Data Store connector backing the live MTG basemap (explicit
user request "je veux que toutes les maps affiché soient des maps du
mtg"). All real HTTP calls are mocked here (unittest.mock.patch, same
convention as tests/test_aviation_live_source.py) - this project's own
test suite must not depend on live network access or EUMETSAT's own
uptime/rate limits.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from acf.connectors.eumetsat_mtg import (
    MTG_FCI_NORMAL_RESOLUTION,
    EUMETSATMTGConnector,
)

_SEARCH_RESPONSE_OK = {
    "features": [
        {
            "properties": {
                "identifier": "PRODUCT_123",
                "date": "2026-09-05T00:20:03Z/2026-09-05T00:29:35Z",
                "links": {
                    "previews": [
                        {"title": "Quicklook", "href": "https://api.eumetsat.int/fake/browse"},
                    ]
                },
            }
        }
    ]
}


@pytest.fixture
def no_env_credentials(monkeypatch):
    monkeypatch.delenv("EUMETSAT_CONSUMER_KEY", raising=False)
    monkeypatch.delenv("EUMETSAT_CONSUMER_SECRET", raising=False)


def _connector(tmp_path, no_env_credentials=None):
    # env_path pointed at an empty, non-existent file - real env vars
    # (patched per-test via monkeypatch) still take effect; this just
    # keeps a real developer .env on this machine from leaking into the
    # test.
    return EUMETSATMTGConnector(env_path=tmp_path / "does_not_exist.env")


def test_has_credentials_is_false_with_nothing_configured(tmp_path, no_env_credentials):
    connector = _connector(tmp_path)
    assert connector.has_credentials is False


def test_has_credentials_is_true_once_both_env_vars_are_set(tmp_path, monkeypatch):
    monkeypatch.setenv("EUMETSAT_CONSUMER_KEY", "key")
    monkeypatch.setenv("EUMETSAT_CONSUMER_SECRET", "secret")
    connector = _connector(tmp_path)
    assert connector.has_credentials is True


def test_authenticate_returns_none_without_credentials_rather_than_a_fake_token(tmp_path, no_env_credentials):
    connector = _connector(tmp_path)
    assert connector._authenticate() is None


def test_authenticate_real_oauth2_exchange_returns_the_real_token(tmp_path, monkeypatch):
    monkeypatch.setenv("EUMETSAT_CONSUMER_KEY", "key")
    monkeypatch.setenv("EUMETSAT_CONSUMER_SECRET", "secret")
    connector = _connector(tmp_path)

    token_response = MagicMock()
    token_response.json.return_value = {"access_token": "real-token-abc", "expires_in": 3600}
    token_response.raise_for_status.return_value = None

    with patch("acf.connectors.eumetsat_mtg.requests.post", return_value=token_response) as mock_post:
        token = connector._authenticate()

    assert token == "real-token-abc"
    # Real client_credentials exchange, real Basic Auth with the
    # configured key/secret - not fabricated.
    _, kwargs = mock_post.call_args
    assert kwargs["auth"] == ("key", "secret")
    assert kwargs["data"] == {"grant_type": "client_credentials"}


def test_authenticate_failure_is_honest_not_a_fabricated_token(tmp_path, monkeypatch):
    monkeypatch.setenv("EUMETSAT_CONSUMER_KEY", "key")
    monkeypatch.setenv("EUMETSAT_CONSUMER_SECRET", "secret")
    connector = _connector(tmp_path)

    with patch("acf.connectors.eumetsat_mtg.requests.post", side_effect=ConnectionError("no route")):
        token = connector._authenticate()

    assert token is None


def test_fetch_latest_image_real_success_path(tmp_path, no_env_credentials):
    connector = _connector(tmp_path)

    search_response = MagicMock()
    search_response.json.return_value = _SEARCH_RESPONSE_OK
    search_response.raise_for_status.return_value = None

    image_response = MagicMock()
    image_response.content = b"fake-jpeg-bytes"
    image_response.raise_for_status.return_value = None

    with patch("acf.connectors.eumetsat_mtg.requests.get", side_effect=[search_response, image_response]) as mock_get:
        result = connector.fetch_latest_image()

    assert result.is_real_data is True
    assert result.status == "FETCHED_OK"
    assert result.image_bytes == b"fake-jpeg-bytes"
    assert result.product_id == "PRODUCT_123"
    assert result.collection == MTG_FCI_NORMAL_RESOLUTION
    assert result.observation_start == "2026-09-05T00:20:03Z"
    assert result.observation_end == "2026-09-05T00:29:35Z"
    assert result.authenticated is False  # no credentials configured
    # Real collection ID actually sent, not a placeholder.
    search_call = mock_get.call_args_list[0]
    assert search_call.kwargs["params"]["pi"] == MTG_FCI_NORMAL_RESOLUTION


def test_fetch_latest_image_honest_when_search_itself_fails(tmp_path, no_env_credentials):
    connector = _connector(tmp_path)
    with patch("acf.connectors.eumetsat_mtg.requests.get", side_effect=ConnectionError("no route")):
        result = connector.fetch_latest_image()
    assert result.is_real_data is False
    assert result.status.startswith("NOT_FETCHED_SEARCH_FAILED")
    assert result.image_bytes is None


def test_fetch_latest_image_honest_when_no_products_returned(tmp_path, no_env_credentials):
    connector = _connector(tmp_path)
    empty_response = MagicMock()
    empty_response.json.return_value = {"features": []}
    empty_response.raise_for_status.return_value = None

    with patch("acf.connectors.eumetsat_mtg.requests.get", return_value=empty_response):
        result = connector.fetch_latest_image()

    assert result.is_real_data is False
    assert result.status == "NOT_FETCHED_NO_PRODUCTS_RETURNED"


def test_fetch_latest_image_honest_when_no_quicklook_link_present(tmp_path, no_env_credentials):
    connector = _connector(tmp_path)
    response = MagicMock()
    response.json.return_value = {
        "features": [{"properties": {"identifier": "P", "date": "a/b", "links": {"previews": []}}}]
    }
    response.raise_for_status.return_value = None

    with patch("acf.connectors.eumetsat_mtg.requests.get", return_value=response):
        result = connector.fetch_latest_image()

    assert result.is_real_data is False
    assert result.status == "NOT_FETCHED_NO_QUICKLOOK_LINK"


def test_fetch_latest_image_honest_when_the_quicklook_download_fails(tmp_path, no_env_credentials):
    connector = _connector(tmp_path)
    search_response = MagicMock()
    search_response.json.return_value = _SEARCH_RESPONSE_OK
    search_response.raise_for_status.return_value = None

    with patch(
        "acf.connectors.eumetsat_mtg.requests.get",
        side_effect=[search_response, ConnectionError("no route")],
    ):
        result = connector.fetch_latest_image()

    assert result.is_real_data is False
    assert result.status.startswith("NOT_FETCHED_DOWNLOAD_FAILED")
