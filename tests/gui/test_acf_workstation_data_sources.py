"""
Tests for the real "Data Sources" nav section added to
acf.gui.dashboard.acf_workstation.ACFWorkstation (Phase 31, 2026-09-04,
matching the reference mockup's own left-column "DATA SOURCES" block).

Each dialog is genuinely modal (`QDialog.exec()`) in production; tests
monkeypatch `QDialog.exec` to capture the constructed dialog instead of
blocking, then inspect its real content directly.
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication, QDialog, QListWidgetItem, QTableWidget, QTextEdit

from acf.forecast.engine import MODEL_CONFIGS
from acf.gui.dashboard.acf_workstation import ACFWorkstation
from acf.science.encyclopedia.registry import EncyclopediaRegistry


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


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


def test_observations_dialog_is_an_honest_not_connected_disclosure(qapp, monkeypatch):
    captured = _capture_dialog(monkeypatch)
    ws = ACFWorkstation()

    ws._on_data_source_selected(QListWidgetItem("Observations"))

    dialog = captured["dialog"]
    label = dialog.layout().itemAt(0).widget()
    assert "No real observation feed" in label.text()


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
