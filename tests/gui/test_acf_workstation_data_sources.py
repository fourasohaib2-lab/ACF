"""
Tests for the real "Data Sources" nav section added to
acf.gui.dashboard.acf_workstation.ACFWorkstation (Phase 31, 2026-09-04,
matching the reference mockup's own left-column "DATA SOURCES" block).

Each dialog is genuinely modal (`QDialog.exec()`) in production; tests
monkeypatch `QDialog.exec` to capture the constructed dialog instead of
blocking, then inspect its real content directly.
"""

from __future__ import annotations

import urllib.error
from unittest.mock import patch

import pytest
import requests
from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import QApplication, QDialog, QListWidgetItem, QTableWidget, QTextEdit

from acf.connectors.eumetsat_mtg import EUMETSATMTGConnector, MTGFetchResult
from acf.forecast.engine import MODEL_CONFIGS
from acf.gui.dashboard.acf_workstation import ACFWorkstation
from acf.gui.map.mtg_basemap import MTGBasemapProvider
from acf.science.encyclopedia.registry import EncyclopediaRegistry


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture(autouse=True)
def _block_real_network_for_observations_dialog():
    """Same convention as tests/test_esoc_earth_monitoring_panel.py -
    the Observations dialog reuses those exact same real connectors, so
    this suite must not depend on live external network access."""
    MTGBasemapProvider._instance = None
    honest_stub = MTGFetchResult(is_real_data=False, status="NOT_FETCHED_YET", authenticated=False)
    service_unavailable = requests.Response()
    service_unavailable.status_code = 503
    with (
        patch.object(EUMETSATMTGConnector, "fetch_latest_image", return_value=honest_stub),
        patch.object(requests, "get", return_value=service_unavailable),
        patch("urllib.request.urlopen", side_effect=urllib.error.URLError("blocked for tests")),
    ):
        yield
    QThreadPool.globalInstance().waitForDone(2000)
    MTGBasemapProvider._instance = None


def _capture_dialog(monkeypatch):
    captured: dict[str, QDialog] = {}

    def fake_exec(self: QDialog) -> int:
        captured["dialog"] = self
        return 0

    monkeypatch.setattr(QDialog, "exec", fake_exec)
    return captured


def test_model_data_dialog_shows_the_real_model_configs(qapp, monkeypatch):
    captured = _capture_dialog(monkeypatch)
    ws = ACFWorkstation()

    ws._on_data_source_selected(QListWidgetItem("Model Data"))

    dialog = captured["dialog"]
    table = dialog.findChild(QTableWidget)
    assert table is not None
    assert table.rowCount() == len(MODEL_CONFIGS)  # real AROME/ALADIN/ARPEGE, never invented
    shown_models = {table.item(row, 0).text() for row in range(table.rowCount())}
    assert shown_models == set(MODEL_CONFIGS.keys())


def test_observations_dialog_shows_the_4_real_feeds_honestly(qapp, monkeypatch):
    """CORRECTED (2026-09-06): this dialog used to unconditionally state
    "No real observation feed is connected" - true when written, stale
    once ESOC's Earth Monitoring panel (same session, Phases 57-60)
    wired 4 real feeds this dialog never learned about. Now reuses those
    exact same connectors/workers rather than continuing to assert a
    now-false claim."""
    captured = _capture_dialog(monkeypatch)
    ws = ACFWorkstation()

    ws._on_data_source_selected(QListWidgetItem("Observations"))
    QThreadPool.globalInstance().waitForDone(2000)
    qapp.processEvents()  # deliver the queued cross-thread `finished` signals

    dialog = captured["dialog"]
    table = dialog.findChild(QTableWidget)
    assert table is not None
    assert table.rowCount() == 4
    feed_names = {table.item(row, 0).text() for row in range(4)}
    assert feed_names == {
        "GOES/MTG Satellites",
        "ARGO Ocean Floats",
        "Surface AWS (SYNOP/METAR)",
        "Doppler Radar (NEXRAD)",
    }
    # The autouse fixture blocks every real network call, so every
    # status must honestly reflect that - never a fabricated LIVE state.
    for row in range(4):
        assert "LIVE" not in table.item(row, 1).text()


def test_scientific_explorer_dialog_searches_the_real_encyclopedia(qapp, monkeypatch):
    captured = _capture_dialog(monkeypatch)
    ws = ACFWorkstation()

    ws._on_data_source_selected(QListWidgetItem("Scientific Explorer"))

    dialog = captured["dialog"]
    assert str(EncyclopediaRegistry.count()) in dialog.windowTitle()
    results = dialog.findChild(QTextEdit)
    assert results is not None
    # Unfiltered: shows real entries (never empty given the real, populated registry).
    assert results.toPlainText() != "No matching real entries."

    # A real, specific search narrows to a genuine subset.
    from PySide6.QtWidgets import QLineEdit

    search_box = dialog.findChild(QLineEdit)
    assert search_box is not None
    search_box.setText("zzz_no_such_real_entry_zzz")
    assert results.toPlainText() == "No matching real entries."
