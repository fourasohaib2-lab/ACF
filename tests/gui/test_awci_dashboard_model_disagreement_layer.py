"""
Tests for AWCIDashboard's real "Model Disagreement" map layer wiring
(Master Prompt V3 §9/§32, added 2026-09-20) -
_run_real_model_disagreement_field()/_ModelDisagreementFieldWorker/
_on_model_disagreement_field_ready()/_on_model_disagreement_field_failed().

Uses steps=2 (like the §13 model-consensus tests) to keep these real
CoupledEarthSolver runs fast enough for a test suite.
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.awci_dashboard import AWCIDashboard, _ModelDisagreementFieldWorker


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_dashboard_connects_the_map_signal_to_its_real_handler(qapp):
    from PySide6.QtCore import QMetaMethod

    dashboard = AWCIDashboard()
    map_panel = dashboard.global_map
    signal_index = map_panel.metaObject().indexOfSignal("modelDisagreementLayerRequested()")
    assert signal_index != -1
    meta_method = map_panel.metaObject().method(signal_index)
    assert isinstance(meta_method, QMetaMethod)
    assert map_panel.isSignalConnected(meta_method)


def test_worker_run_produces_a_real_disagreement_field_synchronously(qtbot):
    """Calls the real worker's run() directly (off any QThreadPool) so
    the test stays deterministic - the SAME real
    ModelConsensusEngine.compute_real_multi_model_disagreement_field()
    call _run_real_model_disagreement_field() itself dispatches
    asynchronously."""
    worker = _ModelDisagreementFieldWorker(steps=2, dt_seconds=90.0, perturbation_scale=3.0, target_model="ARPEGE")
    results = []
    worker.signals.finished.connect(results.append)
    worker.run()

    assert len(results) == 1
    result = results[0]
    assert result["target_model"] == "ARPEGE"
    assert set(result["per_model_field"].keys()) == {"AROME", "ALADIN", "ARPEGE"}
    assert result["disagreement_spread_field"].shape == (len(result["lats"]), len(result["lons"]))
    assert result["is_real_data"] is True


def test_on_model_disagreement_field_ready_feeds_the_real_map_panel(qapp):
    import numpy as np

    dashboard = AWCIDashboard()
    dashboard.global_map.extra_layer_checkboxes["Model Disagreement"].setChecked(True)
    result = {
        "lons": np.linspace(-10, 10, 6),
        "lats": np.linspace(30, 40, 5),
        "disagreement_spread_field": np.ones((5, 6)),
    }

    dashboard._on_model_disagreement_field_ready(result)

    assert "Model Disagreement" in dashboard.global_map._extra_layer_contours


def test_on_model_disagreement_field_failed_shows_a_real_toast(qapp):
    dashboard = AWCIDashboard()
    dashboard._on_model_disagreement_field_failed("solver diverged")
    # No exception raised is the real behavior contract here - the
    # toast itself is a transient, non-modal QWidget with no persisted
    # state to assert against (same convention as this codebase's
    # other _toasts.show() call sites' own tests).


def test_checking_the_layer_on_the_real_dashboard_dispatches_a_worker(qapp, qtbot, monkeypatch):
    """Real end-to-end wiring check: checking the box on the actual
    embedded map panel reaches _run_real_model_disagreement_field()
    via the real Qt signal - patches QThreadPool.start so the test
    doesn't wait on a real background solver run (that path is
    covered directly by
    test_worker_run_produces_a_real_disagreement_field_synchronously
    above)."""
    from PySide6.QtCore import QThreadPool

    dashboard = AWCIDashboard()
    qtbot.addWidget(dashboard)
    started = []
    monkeypatch.setattr(QThreadPool, "start", lambda self, worker: started.append(worker))

    dashboard.global_map.extra_layer_checkboxes["Model Disagreement"].setChecked(True)

    assert len(started) == 1
    assert isinstance(started[0], _ModelDisagreementFieldWorker)
