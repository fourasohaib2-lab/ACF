"""
Tests for acf.gui.dashboard.acf_workstation_forecast_consistency_panel.
ACFForecastConsistencyWidget - the real, on-demand multi-model
consistency side panel (Phase 35, 2026-09-05).
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.acf_workstation_forecast_consistency_panel import ACFForecastConsistencyWidget
from acf.visualization.ai_forecast_center.model_consensus_engine import ModelConsensusEngine


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _real_result():
    return ModelConsensusEngine.compute_real_multi_model_disagreement_field(
        models=["ALADIN", "ARPEGE"], steps=2, target_model="ARPEGE", seed=1
    )


def test_starts_with_no_real_result(qapp):
    widget = ACFForecastConsistencyWidget()
    assert widget.status() == {"has_result": False}
    assert "Not yet computed" in widget.status_label.text()


def test_on_ready_stores_the_real_result_and_updates_status(qapp):
    widget = ACFForecastConsistencyWidget()

    widget._on_ready(_real_result())

    assert widget.status()["has_result"] is True
    assert "✅" in widget.status_label.text()
    assert widget.run_button.isEnabled() is True


def test_on_failed_reports_the_real_error_and_reenables_run(qapp):
    widget = ACFForecastConsistencyWidget()
    widget.run_button.setEnabled(False)

    widget._on_failed("boom")

    assert widget.run_button.isEnabled() is True
    assert "failed" in widget.status_label.text().lower()
    assert widget.status()["has_result"] is False


def test_start_genuinely_runs_a_real_off_thread_comparison(qtbot):
    """Drives the actual QThreadPool path, not a direct call - matching
    this Workstation's own established real-worker-test discipline."""
    widget = ACFForecastConsistencyWidget()
    qtbot.addWidget(widget)

    widget.run_button.click()

    qtbot.waitUntil(lambda: widget.status()["has_result"] is True, timeout=15000)
    assert widget.run_button.isEnabled() is True
