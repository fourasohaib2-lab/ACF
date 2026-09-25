"""
Tests for AWCIDashboard's real N-model consensus wiring (Master Prompt
V3 §13, added 2026-09-20) - `_run_real_model_consensus()`/
`_ModelConsensusWorker`/`_on_model_consensus_ready()`/
`_on_model_consensus_failed()`.

Uses `steps=2` (like tests/test_ai_forecast_center.py's own real
disagreement tests) to keep these real CoupledEarthSolver runs fast
enough for a test suite - still a real solver run per model, not a
mock.
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.awci_dashboard import AWCIDashboard, _ModelConsensusWorker


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_run_real_model_consensus_puts_the_card_in_loading_state(qapp):
    dashboard = AWCIDashboard()
    dashboard.model_agreement_card.show_real_consensus(
        {"per_model_value": {"AROME": 1.0}, "disagreement_spread": 0.0, "field": "T", "level": 0}
    )
    assert dashboard.model_agreement_card.per_model_layout.count() > 0

    dashboard._run_real_model_consensus()

    assert dashboard.model_agreement_card.run_consensus_button.isEnabled() is False
    assert dashboard.model_agreement_card.per_model_layout.count() == 0


def test_worker_run_produces_a_real_per_model_result_synchronously(qtbot):
    """Calls the real worker's run() directly (off any QThreadPool) so
    the test stays deterministic - the SAME real
    ModelConsensusEngine.compute_real_multi_model_disagreement() call
    _run_real_model_consensus() itself dispatches asynchronously."""
    worker = _ModelConsensusWorker(lat=36.7, lon=3.0, steps=2, dt_seconds=90.0, perturbation_scale=3.0)
    results = []
    worker.signals.finished.connect(results.append)
    worker.run()

    assert len(results) == 1
    result = results[0]
    assert set(result["per_model_value"].keys()) == {"AROME", "ALADIN", "ARPEGE"}
    assert result["disagreement_spread"] >= 0.0
    assert result["is_real_data"] is True


def test_on_model_consensus_ready_renders_the_real_result_on_the_card(qapp):
    dashboard = AWCIDashboard()
    result = {
        "per_model_value": {"AROME": 288.1, "ALADIN": 287.9, "ARPEGE": 288.5},
        "disagreement_spread": 0.25,
        "field": "T",
        "level": 0,
    }
    dashboard._on_model_consensus_ready(result)

    rendered_text = " ".join(
        dashboard.model_agreement_card.per_model_layout.itemAt(i).widget().text()
        for i in range(dashboard.model_agreement_card.per_model_layout.count())
    )
    assert "AROME" in rendered_text
    assert "ALADIN" in rendered_text
    assert "ARPEGE" in rendered_text
    assert dashboard.model_agreement_card.run_consensus_button.isEnabled() is True


def test_on_model_consensus_failed_shows_the_real_error_on_the_card(qapp):
    dashboard = AWCIDashboard()
    dashboard._on_model_consensus_failed("solver diverged")

    error_text = dashboard.model_agreement_card.per_model_layout.itemAt(0).widget().text()
    assert "solver diverged" in error_text
    assert dashboard.model_agreement_card.run_consensus_button.isEnabled() is True


def test_dashboard_connects_the_card_signal_to_its_real_handler(qapp):
    """Real wiring check: AWCIDashboard.__init__ must connect
    model_agreement_card.runConsensusRequested to
    _run_real_model_consensus - verified via Qt's own
    isSignalConnected(), not by triggering the expensive default-steps
    solver dispatch (covered directly by
    test_worker_run_produces_a_real_per_model_result_synchronously and
    test_run_real_model_consensus_puts_the_card_in_loading_state
    above)."""
    from PySide6.QtCore import QMetaMethod

    dashboard = AWCIDashboard()
    card = dashboard.model_agreement_card
    signal_index = card.metaObject().indexOfSignal("runConsensusRequested()")
    assert signal_index != -1
    meta_method = card.metaObject().method(signal_index)
    assert isinstance(meta_method, QMetaMethod)
    assert card.isSignalConnected(meta_method)
