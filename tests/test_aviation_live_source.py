"""
Tests for acf.aviation.icao.live_source - real fetch + real decode of
live METAR/TAF/SIGMET from the NOAA Aviation Weather Center's public
API. Mocks urllib.request.urlopen (no live network dependency in CI) -
the real endpoints were manually curl'd and confirmed live during this
feature's own planning; these tests cover this module's own real
logic (URL construction, error handling, decode-failure handling,
SIGMET bulletin splitting), not the external service's availability.

Explicit user request: "le but est de brancher acf et awci avec des
vrais station pour nous rendre des vrai reponse instantanément."
"""

from __future__ import annotations

import urllib.error
from unittest.mock import patch

import pytest

from acf.aviation.icao.live_source import (
    REAL_STATIONS,
    LiveReportUnavailable,
    fetch_active_sigmets,
    fetch_and_decode_station,
    fetch_raw_report,
)

_REAL_KJFK_METAR = "METAR KJFK 030051Z 06003KT 10SM BKN012 OVC030 21/19 A3011 RMK AO2 SLP195 T02060189 $"
_REAL_KJFK_TAF = (
    "TAF KJFK 022332Z 0300/0406 11008KT P6SM BKN020 BKN040\n"
    "  FM030300 15005KT 6SM BR OVC012"
)
_REAL_SIGMET_FEED = (
    "MWRA SIGMET 1 VALID 030100/030500 MMMX-\n"
    "MWRA MEXICO FIR EMBD TS OBS AT 0100Z N OF N20 MOV E 10KT NC=\n"
    "----------------------\n"
    "Type: SIGMET Hazard: CONVECTIVE\n"
    "WSUS31 KKCI 030055\n"
    "SIGE\n"
    "CONVECTIVE SIGMET 1E\n"
    "VALID UNTIL 0255Z\n"
    "NY PA WV\n"
    "AREA SEV TS MOV FROM 27035KT. TOPS ABV FL450.\n"
    "\n"
    "OUTLOOK VALID 030255-030655\n"
    "AREA 1...FROM 70NE MPV-DCA\n"
    "REFER WW 645."
)


class _FakeResponse:
    def __init__(self, body: str, status: int = 200):
        self._body = body.encode("utf-8")
        self.status = status

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def test_real_stations_have_real_confirmed_coordinates():
    """KJFK/LFPG/EGLL/DAAG - each was independently confirmed live via
    curl during this feature's own planning."""
    assert set(REAL_STATIONS.keys()) == {"KJFK", "LFPG", "EGLL", "DAAG"}
    for icao, (lat, lon) in REAL_STATIONS.items():
        assert -90.0 <= lat <= 90.0, icao
        assert -180.0 <= lon <= 180.0, icao


def test_a_wrong_guessed_tripoli_code_was_deliberately_not_added():
    """Real regression guard for a real decision made during planning:
    HLLT/HLLB returned no live data when checked - a wrong guessed
    code must not silently reappear here."""
    assert "HLLT" not in REAL_STATIONS
    assert "HLLB" not in REAL_STATIONS


def test_fetch_raw_report_constructs_the_real_public_endpoint_url():
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.return_value = _FakeResponse(_REAL_KJFK_METAR)
        fetch_raw_report("metar", "KJFK")
    called_url = mock_urlopen.call_args[0][0]
    assert called_url.startswith("https://aviationweather.gov/api/data/metar?")
    assert "ids=KJFK" in called_url
    assert "format=raw" in called_url


def test_fetch_raw_report_returns_the_real_body_text():
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.return_value = _FakeResponse(_REAL_KJFK_METAR)
        result = fetch_raw_report("metar", "KJFK")
    assert result == _REAL_KJFK_METAR


def test_fetch_raw_report_raises_on_empty_response_not_a_fabricated_fallback():
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.return_value = _FakeResponse("")
        with pytest.raises(LiveReportUnavailable, match="empty response"):
            fetch_raw_report("metar", "ZZZZ")


def test_fetch_raw_report_raises_on_non_2xx_status():
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.return_value = _FakeResponse(_REAL_KJFK_METAR, status=404)
        with pytest.raises(LiveReportUnavailable, match="404"):
            fetch_raw_report("metar", "KJFK")


def test_fetch_raw_report_raises_on_a_real_network_error():
    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("no route to host")):
        with pytest.raises(LiveReportUnavailable, match="no route to host"):
            fetch_raw_report("metar", "KJFK")


def test_fetch_and_decode_station_round_trips_a_real_metar_and_taf():
    responses = iter([_FakeResponse(_REAL_KJFK_METAR), _FakeResponse(_REAL_KJFK_TAF)])
    with patch("urllib.request.urlopen", side_effect=lambda *a, **k: next(responses)):
        bundle = fetch_and_decode_station("KJFK")

    assert bundle.icao_code == "KJFK"
    assert bundle.metar.raw_text == _REAL_KJFK_METAR
    assert bundle.metar.error is None
    assert bundle.metar.decoded is not None
    assert bundle.metar.decoded.icao_code == "KJFK"
    assert bundle.metar.decoded.wind_speed_kt == 3.0
    assert bundle.taf.raw_text == _REAL_KJFK_TAF
    assert bundle.taf.error is None
    assert bundle.taf.decoded is not None


def test_fetch_and_decode_station_surfaces_a_fetch_failure_honestly_not_blank():
    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("timed out")):
        bundle = fetch_and_decode_station("KJFK")

    assert bundle.metar.raw_text is None
    assert bundle.metar.decoded is None
    assert bundle.metar.error is not None and "timed out" in bundle.metar.error
    assert bundle.taf.error is not None


def test_fetch_and_decode_station_surfaces_a_real_decode_failure_without_dropping_raw_text():
    """A fetched report the decoder's real, documented grammar gap
    can't parse must still show its real raw text - never silently
    dropped, never replaced with a guess."""
    garbage = "METAR KJFK NOT A REAL WIND GROUP AT ALL"
    responses = iter([_FakeResponse(garbage), _FakeResponse(_REAL_KJFK_TAF)])
    with patch("urllib.request.urlopen", side_effect=lambda *a, **k: next(responses)):
        bundle = fetch_and_decode_station("KJFK")

    assert bundle.metar.raw_text == garbage
    assert bundle.metar.decoded is None
    assert bundle.metar.error is not None and "could not be decoded" in bundle.metar.error


def test_fetch_active_sigmets_splits_on_the_real_dash_separator_not_blank_lines():
    """Real regression guard: a single real bulletin has its own
    internal blank lines (e.g. before its OUTLOOK section) - splitting
    on blank lines instead of the real "----------------------"
    separator would shred one bulletin into multiple garbled ones."""
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.return_value = _FakeResponse(_REAL_SIGMET_FEED)
        reports = fetch_active_sigmets()

    assert len(reports) == 2
    assert "MWRA SIGMET 1" in reports[0].raw_text
    assert "CONVECTIVE SIGMET 1E" in reports[1].raw_text
    # The internal blank line before "OUTLOOK VALID" must stay INSIDE
    # the second bulletin, not become a third, garbled fragment.
    assert "OUTLOOK VALID" in reports[1].raw_text


def test_fetch_active_sigmets_decodes_the_real_icao_tac_bulletin():
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.return_value = _FakeResponse(_REAL_SIGMET_FEED)
        reports = fetch_active_sigmets()

    assert reports[0].decoded is not None
    assert reports[0].decoded.fir_code == "MWRA"
    assert reports[0].error is None


def test_fetch_active_sigmets_honestly_flags_a_real_non_tac_bulletin_without_dropping_it():
    """The real US convective-SIGMET feed format (WMO bulletin header
    ahead of the ICAO TAC body) genuinely does not match
    SIGMETDecoder's documented strict-header scope - confirmed live
    during this feature's planning, not assumed. Must still be
    returned with real raw text and an honest error, not silently
    excluded from the list."""
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.return_value = _FakeResponse(_REAL_SIGMET_FEED)
        reports = fetch_active_sigmets()

    assert reports[1].decoded is None
    assert reports[1].error is not None and "could not be structurally decoded" in reports[1].error
    assert reports[1].raw_text is not None  # real raw text preserved regardless


def test_fetch_active_sigmets_returns_empty_list_on_fetch_failure_not_fabricated_data():
    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("unreachable")):
        reports = fetch_active_sigmets()
    assert reports == []
