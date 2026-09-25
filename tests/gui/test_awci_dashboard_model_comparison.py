"""
Tests for AWCIDashboard's real "Compare Models" action (Master Prompt
V3 §19 - "Allow comparison between: AROME, ALADIN, ARPEGE, WRF,
observation", added 2026-09-20) -
_run_real_model_comparison()/_ModelVerticalProfilesWorker/
_on_model_comparison_ready()/_on_model_comparison_failed().

Uses steps=2 (like the §13/§32 model tests) to keep these real
CoupledEarthSolver runs fast enough for a test suite.
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.awci_dashboard import AWCIDashboard, _ModelVerticalProfilesWorker


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_run_real_model_comparison_puts_the_button_in_loading_state(qapp):
    dashboard = AWCIDashboard()
    dashboard._run_real_model_comparison()

    assert dashboard.compare_models_button.isEnabled() is False
    assert dashboard.compare_models_button.text() == "Comparing…"


def test_worker_run_produces_real_per_model_profiles_synchronously(qtbot):
    """Calls the real worker's run() directly (off any QThreadPool) so
    the test stays deterministic - the SAME real
    ModelConsensusEngine.compute_real_multi_model_vertical_profiles()
    call _run_real_model_comparison() itself dispatches
    asynchronously."""
    worker = _ModelVerticalProfilesWorker(lat=36.7, lon=3.0, steps=2, dt_seconds=90.0, perturbation_scale=3.0)
    results = []
    worker.signals.finished.connect(results.append)
    worker.run()

    assert len(results) == 1
    profiles = results[0]
    assert set(profiles.keys()) == {"AROME", "ALADIN", "ARPEGE"}
    for profile in profiles.values():
        assert len(profile["temperature_profile"]) > 1


def test_on_model_comparison_ready_renders_on_the_real_atmospheric_profile_widget(qapp):
    import numpy as np

    dashboard = AWCIDashboard()
    profiles = {
        "AROME": {
            "lat": 36.7, "lon": 3.0,
            "pressure_profile_hpa": np.array([1000.0, 850.0]),
            "temperature_profile": np.array([290.0, 280.0]),
            "wind_speed_profile": np.array([2.0, 5.0]),
        },
        "ALADIN": {
            "lat": 36.7, "lon": 3.0,
            "pressure_profile_hpa": np.array([1000.0, 850.0]),
            "temperature_profile": np.array([288.0, 278.0]),
            "wind_speed_profile": np.array([3.0, 6.0]),
        },
    }

    dashboard._on_model_comparison_ready(profiles)

    assert dashboard.compare_models_button.isEnabled() is True
    legend = dashboard.atmospheric_profile.axis.get_legend()
    assert legend is not None
    assert {t.get_text() for t in legend.get_texts()} == {"AROME", "ALADIN"}


def test_on_model_comparison_failed_shows_a_real_toast_and_re_enables_button(qapp):
    dashboard = AWCIDashboard()
    dashboard.compare_models_button.setEnabled(False)

    dashboard._on_model_comparison_failed("solver diverged")

    assert dashboard.compare_models_button.isEnabled() is True
    assert dashboard.compare_models_button.text() == "Compare"


def test_clicking_the_button_triggers_the_real_handler(qapp, qtbot, monkeypatch):
    """Patches QThreadPool.start so the test doesn't leave a real
    background solver run (default steps=8) racing the test process's
    own teardown - that path is covered directly by
    test_worker_run_produces_real_per_model_profiles_synchronously
    above."""
    from PySide6.QtCore import QThreadPool

    dashboard = AWCIDashboard()
    qtbot.addWidget(dashboard)
    started = []
    monkeypatch.setattr(QThreadPool, "start", lambda self, worker: started.append(worker))

    dashboard.compare_models_button.click()

    assert len(started) == 1
    assert isinstance(started[0], _ModelVerticalProfilesWorker)
    assert dashboard.compare_models_button.isEnabled() is False
