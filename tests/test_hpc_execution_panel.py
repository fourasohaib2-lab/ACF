"""Unit test suite for HPCExecutionPanel (ACF-HPC-004)."""

import pytest
from PySide6.QtWidgets import QApplication, QTableWidgetItem

from acf.gui.esoc.hpc_execution_panel import HPCExecutionPanel


@pytest.fixture(scope="session")
def qapp():
    """Ensure a PySide6 QApplication instance exists for Qt widget tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_panel_constructs_with_empty_job_table(qapp):
    panel = HPCExecutionPanel()
    assert panel.table.rowCount() == 0


def test_restart_run_failure_is_logged_not_swallowed_silently(qapp, caplog):
    """
    CORRECTED: _on_restart_run() used to catch any exception from
    self.runner.restart(job_id) - e.g. the real KeyError raised for a
    job_id no longer in active_runs - and discard it completely
    silently: the table just refreshed with no indication the restart
    had failed. An operator clicking Restart on a stale/unknown job had
    no way to tell success from failure. Must now be logged (this panel
    has no dedicated status widget to surface it in the UI itself), and
    must not crash the panel either way.
    """
    panel = HPCExecutionPanel()

    # Manually seed a table row referencing a job_id that genuinely does
    # not exist in runner.active_runs, guaranteeing restart() raises.
    panel.table.setRowCount(1)
    panel.table.setItem(0, 0, QTableWidgetItem("nonexistent_job_id_12345"))
    panel.table.setCurrentCell(0, 0)

    with caplog.at_level("ERROR", logger="acf.gui.esoc"):
        panel._on_restart_run()  # must not raise

    assert any("nonexistent_job_id_12345" in r.message for r in caplog.records)
