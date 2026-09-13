from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.acf_workstation_footer import SystemFooterPanel


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


def test_footer_shows_real_hpc_status(qapp, qtbot):
    panel = SystemFooterPanel()
    qtbot.addWidget(panel)
    hpc = MagicMock()
    hpc.get_status_summary.return_value = {
        "connected": True,
        "scheduler": "Slurm",
        "execution_mode": "REAL",
        "operational_mode": "OPERATIONAL",
        "active_jobs_count": 3,
        "telemetry": {},
        "gpu_info": {},
        "mpi_info": {},
    }
    panel.update_from_hpc(hpc)
    assert "Slurm" in panel.system_status_label.text() or "connected" in panel.system_status_label.text().lower()
    assert "3" in panel.running_jobs_label.text()


def test_footer_shows_not_connected_when_hpc_disconnected(qapp, qtbot):
    panel = SystemFooterPanel()
    qtbot.addWidget(panel)
    hpc = MagicMock()
    hpc.get_status_summary.return_value = {
        "connected": False,
        "scheduler": "Slurm",
        "execution_mode": "REAL",
        "operational_mode": "STANDBY",
        "active_jobs_count": 0,
        "telemetry": {},
        "gpu_info": {},
        "mpi_info": {},
    }
    panel.update_from_hpc(hpc)
    text = panel.system_status_label.text().lower()
    assert "not connected" in text or "disconnected" in text
    assert "connected —" not in text.replace("not connected —", "")


def test_footer_default_state_is_not_connected_before_any_update(qapp, qtbot):
    panel = SystemFooterPanel()
    qtbot.addWidget(panel)
    text = panel.system_status_label.text().lower()
    assert "not connected" in text or "disconnected" in text or "not_connected" in text
    assert "connected" not in text.replace("not connected", "").replace("disconnected", "")


def test_footer_appends_activity_log_lines(qapp, qtbot):
    panel = SystemFooterPanel()
    qtbot.addWidget(panel)
    panel.append_activity("AROME forecast completed (+12h)")
    assert "AROME forecast completed" in panel.activity_log.toPlainText()
