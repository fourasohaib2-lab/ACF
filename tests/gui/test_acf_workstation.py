"""
Tests for acf.gui.dashboard.acf_workstation.ACFWorkstation - the real,
AWCI-free "ACF Scientific Workstation" dashboard (added 2026-09-04,
explicit user master spec: "ACF CORE ONLY - NO AWCI"). Chrome +
Overview/Dynamics/Thermodynamics/Complexity Explorer, all sliced from
a single real `compute_real_complexity_volume()` run.

The background-thread plumbing (QThreadPool/_VolumeWorker) is standard,
trusted Qt machinery for most tests here - `test_refresh_genuinely_
runs_a_real_off_thread_volume_run` drives it end-to-end for real (same
discipline as test_acf_general_dashboard.py's own real-worker test);
the rest call `_on_volume_ready()` directly with a small real
precomputed volume, the same way a completed worker signal would
deliver it.
"""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from acf.awci.vertical_field import compute_real_complexity_volume
from acf.forecast.engine import MODEL_CONFIGS
from acf.gui.dashboard.acf_workstation import ACFWorkstation, _ENABLED_MODULES, _PLANNED_MODULES


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _real_volume(**overrides):
    kwargs = dict(model="ALADIN", n_lat=10, n_lon=18, n_levels=5, steps=3, perturbation_scale=2.0, seed=1)
    kwargs.update(overrides)
    return compute_real_complexity_volume(**kwargs)


def test_starts_inert_no_auto_computation(qapp):
    """Real, disclosed choice (matching AWCIDashboard/ACFGeneralDashboard's
    own constructors) - construction alone must not start a real
    background computation."""
    ws = ACFWorkstation()
    assert ws._volume is None
    assert "Not yet computed" in ws.status_label.text()


def test_model_selector_lists_the_real_model_configs(qapp):
    ws = ACFWorkstation()
    real_names = {ws.model_selector.itemText(i) for i in range(ws.model_selector.count())}
    assert real_names == set(MODEL_CONFIGS.keys())  # real AROME/ALADIN/ARPEGE, never invented


def test_nav_lists_the_real_enabled_modules_and_the_rest_disabled(qapp):
    ws = ACFWorkstation()
    enabled_labels = []
    disabled_labels = []
    for i in range(ws.nav_list.count()):
        item = ws.nav_list.item(i)
        is_enabled = bool(item.flags() & Qt.ItemFlag.ItemIsEnabled)
        (enabled_labels if is_enabled else disabled_labels).append(item.text())

    assert enabled_labels == _ENABLED_MODULES
    assert len(disabled_labels) == len(_PLANNED_MODULES)
    for planned in _PLANNED_MODULES:
        assert any(planned in label for label in disabled_labels)


def test_nav_selection_switches_the_real_stacked_content(qapp):
    ws = ACFWorkstation()
    assert ws.stack.currentWidget() is ws.overview_panel

    ws.nav_list.setCurrentRow(1)
    assert ws.stack.currentWidget() is ws.dynamics_panel

    ws.nav_list.setCurrentRow(2)
    assert ws.stack.currentWidget() is ws.thermodynamics_panel

    ws.nav_list.setCurrentRow(3)
    assert ws.stack.currentWidget() is ws.microphysics_panel

    ws.nav_list.setCurrentRow(4)
    assert ws.stack.currentWidget() is ws.temporal_panel

    ws.nav_list.setCurrentRow(5)
    assert ws.stack.currentWidget() is ws.confidence_panel

    ws.nav_list.setCurrentRow(6)
    assert ws.stack.currentWidget() is ws.multimodel_panel

    ws.nav_list.setCurrentRow(7)
    assert ws.stack.currentWidget() is ws.interactions_panel

    ws.nav_list.setCurrentRow(8)
    assert ws.stack.currentWidget() is ws.quality_panel

    ws.nav_list.setCurrentRow(9)
    assert ws.stack.currentWidget() is ws.complexity_panel

    ws.nav_list.setCurrentRow(10)
    assert ws.stack.currentWidget() is ws.atmosphere_3d_panel

    ws.nav_list.setCurrentRow(11)
    assert ws.stack.currentWidget() is ws.case_study_panel

    ws.nav_list.setCurrentRow(12)
    assert ws.stack.currentWidget() is ws.convection_panel


def test_on_volume_ready_populates_the_level_slider_and_every_panel(qapp):
    ws = ACFWorkstation()
    volume = _real_volume()

    ws._on_volume_ready(volume)

    assert ws.level_slider.isEnabled()
    assert ws.level_slider.maximum() == volume["n_levels"] - 1
    assert "hPa" in ws.level_label.text()
    assert "✅" in ws.status_label.text()
    assert "20241027" not in ws.status_label.text()  # never a fabricated forecast run-ID
    assert ws.overview_panel._volume is volume
    assert ws.dynamics_panel._volume is volume
    assert ws.thermodynamics_panel._volume is volume
    assert ws.microphysics_panel._volume is volume
    assert ws.temporal_panel._volume is volume
    assert ws.confidence_panel._volume is volume
    assert ws.multimodel_panel._volume is volume
    assert ws.interactions_panel._volume is volume
    assert ws.quality_panel._volume is volume
    assert ws.complexity_panel._volume is volume
    assert ws.atmosphere_3d_panel._volume is volume
    # ACFCaseStudyLabPanel.update_from_volume() is a real no-op (it
    # manages saved SETTINGS, never volume data) - just confirm the
    # call didn't raise, matching the uniform per-panel call in
    # _render_all_panels().
    assert ws.convection_panel._volume is volume


def test_changing_the_level_slider_reslices_without_a_new_solver_run(qapp, monkeypatch):
    """Real regression guard: switching levels must re-slice the
    already-computed volume, never trigger a second real solver run."""
    ws = ACFWorkstation()
    ws._on_volume_ready(_real_volume())

    call_count = {"n": 0}

    def _fail_if_called(*_args, **_kwargs):
        call_count["n"] += 1
        raise AssertionError("a new solver run must not happen on a level change")

    monkeypatch.setattr("acf.gui.dashboard.acf_workstation.compute_real_complexity_volume", _fail_if_called)

    ws.level_slider.setValue(ws.level_slider.maximum())

    assert call_count["n"] == 0
    assert ws._level_index == ws.level_slider.maximum()


def test_volume_failure_reports_error_and_reenables_run(qapp):
    ws = ACFWorkstation()
    ws.run_button.setEnabled(False)

    ws._on_volume_failed("boom")

    assert ws.run_button.isEnabled() is True
    assert "failed" in ws.status_label.text().lower()


def test_refresh_genuinely_runs_a_real_off_thread_volume_run(qtbot):
    """Drives the actual QThreadPool.globalInstance().start() + Qt event
    loop path, not a direct call."""
    ws = ACFWorkstation()
    qtbot.addWidget(ws)
    ws.model_selector.setCurrentText("ARPEGE")  # the real default, smallest of the 3 real MODEL_CONFIGS grids

    ws.refresh()

    qtbot.waitUntil(lambda: ws._volume is not None, timeout=60000)
    assert ws.overview_panel.map_panel._contour is not None
    assert "✅" in ws.status_label.text()
