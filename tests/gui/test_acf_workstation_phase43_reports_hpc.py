"""
Tests for ACF Scientific Workstation's Phase 43 (2026-09-12) "REPORTS"
and "HPC / JOBS" nav sections - added to match the new "Atmospheric
Analysis" reference mockup's own nav taxonomy, after the user chose full
replacement over a reskin-only or parallel-view alternative.

"Export Configuration Report" reuses the real, already-tested
_save_configuration() (no second implementation, no fabricated report
content). "Connect to HPC Cluster" reuses ESOC's own real
HPCConnectionDialog + HPCConnectionManager (the exact same real,
off-thread SSH connect flow ESOCWindow._connect_hpc() already uses).
"""

from __future__ import annotations

import json

import pytest
from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import QApplication, QFileDialog

from acf.gui.dashboard.acf_workstation import ACFWorkstation
from acf.gui.esoc.hpc_connection_dialog import HPCConnectionDialog


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


# --------------------------------------------------------------- REPORTS


def test_export_report_button_exists_with_an_honest_tooltip(qapp):
    ws = ACFWorkstation()

    assert ws.export_report_button.text() == "📄 Export Configuration Report"
    tooltip = ws.export_report_button.toolTip()
    assert "not a generated PDF/HTML report" in tooltip


def test_export_report_button_genuinely_calls_the_real_save_configuration(qapp, tmp_path, monkeypatch):
    ws = ACFWorkstation()
    ws.model_selector.setCurrentText("ALADIN")
    target = tmp_path / "report.json"
    monkeypatch.setattr(QFileDialog, "getSaveFileName", staticmethod(lambda *a, **k: (str(target), "")))

    ws.export_report_button.click()

    assert target.exists()
    payload = json.loads(target.read_text(encoding="utf-8"))
    assert payload["model"] == "ALADIN"
    assert "✅" in ws.status_label.text()


# --------------------------------------------------------------- HPC/JOBS


def test_hpc_section_starts_disconnected_and_honest(qapp):
    ws = ACFWorkstation()

    assert ws.hpc_status_label.text() == "Not connected."
    assert ws.hpc_connect_button.isEnabled() is True


def test_hpc_connect_button_does_nothing_if_the_dialog_is_cancelled(qapp, monkeypatch):
    ws = ACFWorkstation()
    monkeypatch.setattr(HPCConnectionDialog, "exec", lambda self: HPCConnectionDialog.DialogCode.Rejected)

    ws._connect_to_hpc()

    assert ws.hpc_status_label.text() == "Not connected."


def test_hpc_connect_button_genuinely_runs_off_thread_and_reports_honestly(qapp, monkeypatch):
    """Real regression guard: this environment has no reachable HPC
    cluster, so a genuine connect attempt must honestly report
    "local/offline dev mode", never a fabricated "Connected"."""
    ws = ACFWorkstation()
    monkeypatch.setattr(HPCConnectionDialog, "exec", lambda self: HPCConnectionDialog.DialogCode.Accepted)
    monkeypatch.setattr(
        HPCConnectionDialog,
        "get_connection_config",
        lambda self: {"profile_key": "fennec", "profile_name": "FENNEC"},
    )

    ws._connect_to_hpc()

    assert ws.hpc_connect_button.isEnabled() is False
    assert "Connecting" in ws.hpc_status_label.text()

    QThreadPool.globalInstance().waitForDone(20_000)
    qapp.processEvents()

    assert ws.hpc_connect_button.isEnabled() is True
    assert "local/offline dev mode" in ws.hpc_status_label.text()
    assert "✅ Connected" not in ws.hpc_status_label.text()


# --------------------------------------------- Header clock (ICAO Annex 3 §4.1)


def test_header_clock_shows_genuine_utc_not_local_time(qapp):
    """ICAO Annex 3 §4.1: all aeronautical meteorological information must
    be expressed in UTC, never local time. Regression guard for a real
    fix (2026-09-12): the header clock originally showed local time,
    honestly labelled "(local)" rather than fabricating a "UTC" label on
    a value that wasn't - but the correct fix is a genuine UTC value, not
    an honest disclaimer on a wrong one."""
    ws = ACFWorkstation()

    text = ws.clock_label.text()

    assert text.endswith(" UTC")
    assert "local" not in text.lower()
