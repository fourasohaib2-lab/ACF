"""
Regression tests for 4 button groups in acf.gui.esoc.panel_manager's HPC
panels, found during a full ESOC rescan (2026-09-11): each used to
dispatch a CommandDispatcher command name ("connect_hpc", "disconnect_hpc",
"submit_hpc_job", "cancel_hpc_job", "sync_hpc_storage", "benchmark_hpc")
that was never registered anywhere - CommandDispatcher.dispatch() only
emits an invisible log WARNING for an unregistered command, so clicking
any of these buttons was silent, total inaction. Each now genuinely calls
the real HPCConnectionManager (registry's own "hpc_connector" module)
instead - offline/local-dev-mode outcomes are honestly reported, never
fabricated as a real cluster action.

LocalScheduler (the real default when no cluster profile has been
connected) is itself already honest and side-effect-free (no subprocess,
no network - see scheduler_interface.py's own NOTE), so these tests need
no network mocking.
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication, QFileDialog

from acf.gui.esoc.command_dispatcher import CommandDispatcher
from acf.gui.esoc.module_registry import ModuleRegistry
from acf.gui.esoc.panel_manager import BenchmarkPanel, HPCDashboardPanel, JobExplorerPanel, StorageMonitorPanel


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def registry(qapp):
    return ModuleRegistry()


@pytest.fixture
def dispatcher(qapp):
    return CommandDispatcher()


# ------------------------------------------------------- HPCDashboardPanel


def test_connect_button_genuinely_calls_the_real_hpc_connector(registry, dispatcher, qtbot):
    panel = HPCDashboardPanel(registry, dispatcher)
    qtbot.addWidget(panel)

    panel._connect()

    qtbot.waitUntil(lambda: "Connecting" not in panel.txt_status.toPlainText(), timeout=10000)
    # Local/offline dev mode (no real cluster reachable here) - honestly
    # reported, never claimed as a real connection.
    assert "no real SSH" in panel.txt_status.toPlainText() or "✅" in panel.txt_status.toPlainText()


def test_disconnect_button_genuinely_calls_the_real_disconnect(registry, dispatcher, qtbot):
    panel = HPCDashboardPanel(registry, dispatcher)
    qtbot.addWidget(panel)

    panel._disconnect()

    assert "closed" in panel.txt_status.toPlainText().lower()


def test_connect_button_reports_missing_module_honestly(dispatcher, qtbot):
    registry = ModuleRegistry()
    registry.modules["hpc_connector"] = None
    panel = HPCDashboardPanel(registry, dispatcher)
    qtbot.addWidget(panel)

    panel._connect()

    assert "not available" in panel.txt_status.toPlainText()


# --------------------------------------------------------- JobExplorerPanel


def test_submit_button_genuinely_calls_the_real_job_manager_and_refreshes_table(registry, dispatcher, qtbot):
    panel = JobExplorerPanel(registry, dispatcher)
    qtbot.addWidget(panel)
    assert panel.table.rowCount() == 0  # honest empty state, not a fabricated EXAMPLE row

    panel._submit()

    assert panel.table.rowCount() == 1
    hpc = registry.get_module("hpc_connector")
    expected = hpc.job_manager.list_jobs()[0]
    assert panel.table.item(0, 0).text() == expected["job_id"]
    assert panel.table.item(0, 3).text() == expected["status"]
    # LocalScheduler is the real default here - honestly not a real submission.
    assert "NOT_SUBMITTED" in expected["status"]
    assert "no real scheduler" in panel._status_label.text()


def test_cancel_with_nothing_selected_is_an_honest_no_op(registry, dispatcher, qtbot):
    panel = JobExplorerPanel(registry, dispatcher)
    qtbot.addWidget(panel)

    panel._cancel_selected()

    assert "select a job" in panel._status_label.text().lower()


def test_cancel_selected_row_genuinely_calls_the_real_job_manager(registry, dispatcher, qtbot):
    panel = JobExplorerPanel(registry, dispatcher)
    qtbot.addWidget(panel)
    panel._submit()
    panel.table.setCurrentCell(0, 0)

    panel._cancel_selected()

    # LocalScheduler.cancel_job() honestly returns False (see its own NOTE) -
    # never fabricated as a genuine cancellation.
    assert "could not be confirmed" in panel._status_label.text()


# ------------------------------------------------------- StorageMonitorPanel


def test_sync_button_does_nothing_without_a_real_file_selected(registry, dispatcher, qtbot, monkeypatch):
    panel = StorageMonitorPanel(registry, dispatcher)
    qtbot.addWidget(panel)
    monkeypatch.setattr(QFileDialog, "getOpenFileName", staticmethod(lambda *a, **k: ("", "")))

    panel._sync()

    assert "GPFS Parallel Storage Example Layout" in panel.txt.toPlainText()  # unchanged, no fabricated sync


def test_sync_button_genuinely_calls_the_real_file_transfer_manager(registry, dispatcher, qtbot, monkeypatch, tmp_path):
    real_file = tmp_path / "test_upload.nc"
    real_file.write_bytes(b"not a real netcdf, just bytes for the test")
    panel = StorageMonitorPanel(registry, dispatcher)
    qtbot.addWidget(panel)
    monkeypatch.setattr(QFileDialog, "getOpenFileName", staticmethod(lambda *a, **k: (str(real_file), "")))

    panel._sync()

    # No real SSH transport in this test environment - honestly reported,
    # never claimed as a completed transfer.
    assert "no real transfer was confirmed" in panel.txt.toPlainText()
    assert str(real_file) in panel.txt.toPlainText()


# ------------------------------------------------------------- BenchmarkPanel


def test_benchmark_button_genuinely_calls_the_real_benchmark_and_is_honest_about_no_probe(registry, dispatcher, qtbot):
    panel = BenchmarkPanel(registry, dispatcher)
    qtbot.addWidget(panel)

    panel._run_benchmark()

    # HPCConnectionManager.benchmark_performance() is itself already honest
    # (no stress-ng/mpirun/ib_write_bw/BeeGFS probe wired) - this must
    # reflect that real call's real result, not a fabricated PASSED.
    assert "NOT_BENCHMARKED_NO_LIVE_PROBE_CONNECTED" in panel.txt_bench.toPlainText()
    assert "CPU GFLOPS" not in panel.txt_bench.toPlainText()  # no fabricated numeric result
