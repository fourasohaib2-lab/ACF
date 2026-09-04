"""
Tests for acf.gui.dashboard.acf_workstation_pipeline_monitor.
ACFPipelineMonitorWidget - the real, honest display widget behind the
ACF Scientific Workstation's own "ACF Pipeline Monitor" (Phase 32,
2026-09-05).
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.acf_workstation_pipeline_monitor import STAGES, ACFPipelineMonitorWidget


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_starts_with_every_real_stage_pending(qapp):
    widget = ACFPipelineMonitorWidget()
    assert widget.status_snapshot() == {name: "—" for name in STAGES}


def test_set_stage_updates_the_real_status_and_tooltip(qapp):
    widget = ACFPipelineMonitorWidget()

    widget.set_stage("QC", "WARN", "1 real range violation(s): boom")

    snapshot = widget.status_snapshot()
    assert snapshot["QC"] == "WARN"
    assert snapshot["Ingestion"] == "—"  # untouched stages stay genuinely pending
    assert widget._labels["QC"].toolTip() == "1 real range violation(s): boom"


def test_reset_returns_every_stage_to_pending(qapp):
    widget = ACFPipelineMonitorWidget()
    widget.set_stage("Modules", "OK", "done")

    widget.reset()

    assert widget.status_snapshot() == {name: "—" for name in STAGES}


def test_set_stage_rejects_an_unknown_stage_name(qapp):
    widget = ACFPipelineMonitorWidget()
    with pytest.raises(ValueError, match="Unknown real pipeline stage"):
        widget.set_stage("Not A Real Stage", "OK")
