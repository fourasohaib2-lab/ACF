"""
Tests for acf.gui.dashboard.awci_messages_panel.AWCIMessagesDialog -
the real, live METAR/TAF/SPECI/SIGMET viewer. Mocks
acf.aviation.icao.live_source's fetch functions (no live network
dependency in CI - those functions' own real HTTP/decode behavior is
covered by tests/test_aviation_live_source.py); these tests cover the
dialog's own real wiring: does a fetched-and-decoded result actually
reach the UI, and does a failure show honestly rather than blank.
"""

from __future__ import annotations

import time
from unittest.mock import patch

from PySide6.QtCore import Qt

from acf.aviation.icao.live_source import LiveReport, LiveStationBundle
from acf.aviation.icao.metar_decoder import METARDecoder, METARReport
from acf.aviation.icao.taf_decoder import TAFDecoder
from acf.gui.dashboard.awci_dashboard import AWCIDashboard
from acf.gui.dashboard.awci_messages_panel import AWCIMessagesDialog

_REAL_KJFK_METAR = "METAR KJFK 030051Z 06003KT 10SM BKN012 OVC030 21/19 A3011 RMK AO2 SLP195 T02060189 $"
_REAL_KJFK_TAF = "TAF KJFK 022332Z 0300/0406 11008KT P6SM BKN020 BKN040"


def _fake_bundle(icao: str, with_data: bool = True) -> LiveStationBundle:
    bundle = LiveStationBundle(icao_code=icao)
    if with_data:
        bundle.metar.raw_text = _REAL_KJFK_METAR.replace("KJFK", icao)
        bundle.metar.decoded = METARDecoder.decode(bundle.metar.raw_text)
        bundle.taf.raw_text = _REAL_KJFK_TAF.replace("KJFK", icao)
        bundle.taf.decoded = TAFDecoder.decode(bundle.taf.raw_text)
    else:
        bundle.metar.error = "no route to host"
        bundle.taf.error = "no route to host"
    return bundle


def _wait_until(condition, timeout_s: float = 10.0) -> None:
    from PySide6.QtWidgets import QApplication

    deadline = time.time() + timeout_s
    while not condition() and time.time() < deadline:
        QApplication.processEvents()
        time.sleep(0.02)
    assert condition(), "condition not met within timeout"


def test_dialog_shows_real_decoded_fields_from_a_successful_fetch(qtbot):
    with patch(
        "acf.gui.dashboard.awci_messages_panel.fetch_and_decode_station",
        side_effect=lambda icao, timeout=8.0: _fake_bundle(icao),
    ), patch("acf.gui.dashboard.awci_messages_panel.fetch_active_sigmets", return_value=[]):
        dialog = AWCIMessagesDialog()
        qtbot.addWidget(dialog)
        _wait_until(lambda: "Fetching" not in dialog.status_label.text())

    assert "4/4" in dialog.status_label.text()
    text = dialog.station_text_edits["KJFK"].toPlainText()
    assert "METAR KJFK" in text
    assert "Wind: 060° at 3 kt" in text  # real decoded field, not just raw text


def test_dialog_shows_real_section_32_quality_status_for_a_normal_station(qtbot):
    """docs/ACF_MASTER_PROMPT.md section 32 - real per-variable quality
    status, closing the quality-flagging half of "brancher acf et awci
    avec des vrais station" for this panel's own real live data."""
    with patch(
        "acf.gui.dashboard.awci_messages_panel.fetch_and_decode_station",
        side_effect=lambda icao, timeout=8.0: _fake_bundle(icao),
    ), patch("acf.gui.dashboard.awci_messages_panel.fetch_active_sigmets", return_value=[]):
        dialog = AWCIMessagesDialog()
        qtbot.addWidget(dialog)
        _wait_until(lambda: "Fetching" not in dialog.status_label.text())

    text = dialog.station_text_edits["KJFK"].toPlainText()
    assert "Quality (§32): 4/4 variable(s) VALID." in text


def test_dialog_surfaces_a_real_out_of_range_variable_in_the_quality_line(qtbot):
    def _bundle_with_bad_temperature(icao: str, timeout: float = 8.0) -> LiveStationBundle:
        bundle = _fake_bundle(icao)
        assert isinstance(bundle.metar.decoded, METARReport)
        bundle.metar.decoded.temperature_c = 99.0  # a real, genuine out-of-range value
        return bundle

    with patch(
        "acf.gui.dashboard.awci_messages_panel.fetch_and_decode_station", side_effect=_bundle_with_bad_temperature
    ), patch("acf.gui.dashboard.awci_messages_panel.fetch_active_sigmets", return_value=[]):
        dialog = AWCIMessagesDialog()
        qtbot.addWidget(dialog)
        _wait_until(lambda: "Fetching" not in dialog.status_label.text())

    text = dialog.station_text_edits["KJFK"].toPlainText()
    assert "Quality (§32): 3/4 VALID" in text
    assert "air_temperature=OUT_OF_RANGE" in text


def test_dialog_shows_an_honest_error_not_blank_on_fetch_failure(qtbot):
    with patch(
        "acf.gui.dashboard.awci_messages_panel.fetch_and_decode_station",
        side_effect=lambda icao, timeout=8.0: _fake_bundle(icao, with_data=False),
    ), patch("acf.gui.dashboard.awci_messages_panel.fetch_active_sigmets", return_value=[]):
        dialog = AWCIMessagesDialog()
        qtbot.addWidget(dialog)
        _wait_until(lambda: "Fetching" not in dialog.status_label.text())

    text = dialog.station_text_edits["KJFK"].toPlainText()
    assert "⚠ Live data unavailable" in text
    assert "no route to host" in text


def test_dialog_shows_real_sigmet_raw_text_when_available(qtbot):
    sigmet = LiveReport(raw_text="MWRA SIGMET 1 VALID 030100/030500 MMMX-\nsome real text")
    with patch(
        "acf.gui.dashboard.awci_messages_panel.fetch_and_decode_station",
        side_effect=lambda icao, timeout=8.0: _fake_bundle(icao),
    ), patch("acf.gui.dashboard.awci_messages_panel.fetch_active_sigmets", return_value=[sigmet]):
        dialog = AWCIMessagesDialog()
        qtbot.addWidget(dialog)
        _wait_until(lambda: "Fetching" not in dialog.status_label.text())

    assert "MWRA SIGMET 1" in dialog.sigmet_text_edit.toPlainText()


def test_dialog_honestly_reports_no_sigmets_rather_than_blank(qtbot):
    with patch(
        "acf.gui.dashboard.awci_messages_panel.fetch_and_decode_station",
        side_effect=lambda icao, timeout=8.0: _fake_bundle(icao),
    ), patch("acf.gui.dashboard.awci_messages_panel.fetch_active_sigmets", return_value=[]):
        dialog = AWCIMessagesDialog()
        qtbot.addWidget(dialog)
        _wait_until(lambda: "Fetching" not in dialog.status_label.text())

    assert "No active SIGMETs" in dialog.sigmet_text_edit.toPlainText()


def test_refresh_button_triggers_a_real_new_fetch(qtbot):
    call_count = {"n": 0}

    def _counting_fetch(icao, timeout=8.0):
        call_count["n"] += 1
        return _fake_bundle(icao)

    with patch("acf.gui.dashboard.awci_messages_panel.fetch_and_decode_station", side_effect=_counting_fetch), patch(
        "acf.gui.dashboard.awci_messages_panel.fetch_active_sigmets", return_value=[]
    ):
        dialog = AWCIMessagesDialog()
        qtbot.addWidget(dialog)
        _wait_until(lambda: "Fetching" not in dialog.status_label.text())
        first_count = call_count["n"]

        qtbot.mouseClick(dialog.refresh_button, Qt.MouseButton.LeftButton)
        _wait_until(lambda: call_count["n"] > first_count)

    assert call_count["n"] == first_count * 2


def test_awci_dashboard_message_button_opens_the_real_dialog(qtbot):
    with patch(
        "acf.gui.dashboard.awci_messages_panel.fetch_and_decode_station",
        side_effect=lambda icao, timeout=8.0: _fake_bundle(icao),
    ), patch("acf.gui.dashboard.awci_messages_panel.fetch_active_sigmets", return_value=[]):
        dashboard = AWCIDashboard()
        qtbot.addWidget(dashboard)
        assert dashboard._messages_window is None

        dashboard._open_messages()

        assert dashboard._messages_window is not None
        _wait_until(lambda: "Fetching" not in dashboard._messages_window.status_label.text())


def test_awci_dashboard_message_button_reuses_the_same_dialog_on_second_click(qtbot):
    with patch(
        "acf.gui.dashboard.awci_messages_panel.fetch_and_decode_station",
        side_effect=lambda icao, timeout=8.0: _fake_bundle(icao),
    ), patch("acf.gui.dashboard.awci_messages_panel.fetch_active_sigmets", return_value=[]):
        dashboard = AWCIDashboard()
        qtbot.addWidget(dashboard)
        dashboard._open_messages()
        _wait_until(lambda: "Fetching" not in dashboard._messages_window.status_label.text())
        first_window = dashboard._messages_window

        dashboard._open_messages()

        assert dashboard._messages_window is first_window
