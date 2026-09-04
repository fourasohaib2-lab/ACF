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


def test_overview_landing_panel_is_the_real_first_stack_widget(qapp):
    """Real Phase 31 regression guard (2026-09-04): the reference
    mockup's own nav tree shows a distinct "Overview" above "Atmosphere
    State" - construction alone must land on the real landing page, not
    the raw-fields map panel."""
    ws = ACFWorkstation()
    assert ws.nav_list.item(0).text() == "Overview"
    assert ws.nav_list.item(1).text() == "Atmosphere State"
    assert ws.stack.currentWidget() is ws.overview_landing_panel
    assert ws._panel_by_name["Overview"] is ws.overview_landing_panel
    assert ws._panel_by_name["Atmosphere State"] is ws.overview_panel


def test_model_selector_change_updates_the_real_landing_page(qapp):
    ws = ACFWorkstation()
    ws.model_selector.setCurrentText("AROME")
    config = MODEL_CONFIGS["AROME"]
    assert str(config["n_lat"]) in ws.overview_landing_panel.model_info_label.text()


def test_run_status_mirrors_onto_the_real_landing_page(qapp):
    ws = ACFWorkstation()
    ws._on_volume_ready(_real_volume())
    assert ws.overview_landing_panel.status_label.text() == ws.status_label.text()
    assert "✅" in ws.overview_landing_panel.status_label.text()


def test_data_sources_list_has_the_real_three_entries(qapp):
    ws = ACFWorkstation()
    labels = [ws.data_sources_list.item(i).text() for i in range(ws.data_sources_list.count())]
    assert labels == ["Model Data", "Observations", "Scientific Explorer"]


def test_more_labs_toolbar_reaches_every_real_relocated_module(qapp):
    """Real Phase 31 regression guard: modules moved out of the main
    nav (because the mockup's own tree doesn't show them) must stay
    genuinely reachable - kept, never deleted."""
    from acf.gui.dashboard.acf_workstation import _TOOLBAR_MODULES

    ws = ACFWorkstation()
    assert set(ws.more_labs_actions.keys()) == set(_TOOLBAR_MODULES)
    for name in _TOOLBAR_MODULES:
        ws.more_labs_actions[name].trigger()
        assert ws.stack.currentWidget() is ws._panel_by_name[name]
        assert ws.nav_list.currentRow() == -1


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
    # Real nav order/labels (Phase 31, 2026-09-04) - matches the
    # Workstation's own reference mockup exactly, see _ENABLED_MODULES;
    # routing is name-based (`_panel_by_name`), not row-index-based.
    ws = ACFWorkstation()
    assert ws.stack.currentWidget() is ws.overview_landing_panel

    ws.nav_list.setCurrentRow(1)  # Atmosphere State
    assert ws.stack.currentWidget() is ws.overview_panel

    ws.nav_list.setCurrentRow(2)  # Complexity Explorer
    assert ws.stack.currentWidget() is ws.complexity_panel

    ws.nav_list.setCurrentRow(3)  # Atmospheric Interaction Engine
    assert ws.stack.currentWidget() is ws.interactions_panel

    ws.nav_list.setCurrentRow(4)  # Dynamics Lab
    assert ws.stack.currentWidget() is ws.dynamics_panel

    ws.nav_list.setCurrentRow(5)  # Thermodynamics Lab
    assert ws.stack.currentWidget() is ws.thermodynamics_panel

    ws.nav_list.setCurrentRow(6)  # Convection Lab
    assert ws.stack.currentWidget() is ws.convection_panel

    ws.nav_list.setCurrentRow(7)  # Microphysics Lab
    assert ws.stack.currentWidget() is ws.microphysics_panel

    ws.nav_list.setCurrentRow(8)  # Terrain Lab
    assert ws.stack.currentWidget() is ws.terrain_panel

    ws.nav_list.setCurrentRow(9)  # Temporal Evolution Lab
    assert ws.stack.currentWidget() is ws.temporal_panel

    ws.nav_list.setCurrentRow(10)  # Forecast Consistency Lab
    assert ws.stack.currentWidget() is ws.confidence_panel

    # Real modules the mockup's own nav tree doesn't show - kept,
    # reachable via _navigate_to() (the "🧰 More Labs" toolbar path),
    # never deleted.
    ws._navigate_to("Multi-Model Lab")
    assert ws.stack.currentWidget() is ws.multimodel_panel

    ws._navigate_to("Data Quality Center")
    assert ws.stack.currentWidget() is ws.quality_panel

    ws._navigate_to("3D Atmosphere View")
    assert ws.stack.currentWidget() is ws.atmosphere_3d_panel

    ws._navigate_to("Case Study Lab")
    assert ws.stack.currentWidget() is ws.case_study_panel


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
    assert ws.terrain_panel._volume is volume


def test_on_volume_ready_updates_the_real_pipeline_monitor(qapp):
    """Real Phase 32 regression guard (2026-09-05): the ACF Pipeline
    Monitor's own QC/Normalization/Interactions/Analysis/Visualization
    stages must reflect this real run, never stay pending."""
    ws = ACFWorkstation()
    volume = _real_volume()

    ws._on_volume_ready(volume)

    snapshot = ws.pipeline_monitor.status_snapshot()
    assert snapshot["Modules"] == "OK"
    assert snapshot["QC"] in ("OK", "WARN")  # a real, honest QC verdict either way
    assert snapshot["Normalization"] == "OK"
    assert snapshot["Interactions"] == "OK"
    assert snapshot["Analysis"] == "OK"
    assert snapshot["Visualization"] == "OK"


def test_on_volume_ready_defaults_the_sounding_to_the_real_grid_center(qapp):
    """Real Phase 33 regression guard (2026-09-05): before any real map
    click has happened, the always-visible sounding panel must still
    show a real point (the volume's own grid center), never stay empty."""
    ws = ACFWorkstation()
    volume = _real_volume()

    ws._on_volume_ready(volume)

    assert ws.sounding_panel.status()["has_point"] is True


def test_clicking_any_real_map_updates_the_shared_sounding_panel(qapp):
    """Real Phase 33 regression guard: every Lab panel's own real map
    is wired to the SAME sounding panel, never an independent copy."""
    ws = ACFWorkstation()
    volume = _real_volume()
    ws._on_volume_ready(volume)

    lat, lon = float(volume["lats"][1]), float(volume["lons"][2])
    ws.dynamics_panel.map_panel.pointClicked.emit(lat, lon)

    assert ws._last_clicked_point == (lat, lon)
    assert ws.sounding_panel.status()["point"] == (lat, lon)


def test_on_volume_ready_populates_the_real_interaction_graph(qapp):
    """Real Phase 34 regression guard (2026-09-05): the always-visible
    Atmospheric Interaction Graph must reflect this real run."""
    ws = ACFWorkstation()
    volume = _real_volume()

    ws._on_volume_ready(volume)

    assert ws.interaction_graph_panel.status()["has_edges"] is True


def test_forecast_consistency_panel_is_present_and_starts_uncomputed(qapp):
    """Real Phase 35 regression guard (2026-09-05): the third
    always-visible-slot side panel exists and stays honestly
    "Not yet computed" until its own real on-demand run - it is NOT
    tied to the main "🔄 Run" volume."""
    ws = ACFWorkstation()

    assert ws.forecast_consistency_panel.status() == {"has_result": False}

    ws._on_volume_ready(_real_volume())

    assert ws.forecast_consistency_panel.status() == {"has_result": False}


def test_map_inspector_stays_none_until_a_real_click(qapp):
    """Real Phase 36 regression guard (2026-09-05): the Map Inspector
    is created lazily, never eagerly at construction."""
    ws = ACFWorkstation()
    assert ws._map_inspector is None


def test_clicking_a_real_map_opens_and_fills_the_map_inspector(qapp):
    ws = ACFWorkstation()
    volume = _real_volume()
    ws._on_volume_ready(volume)

    lat, lon = float(volume["lats"][1]), float(volume["lons"][2])
    ws.thermodynamics_panel.map_panel.pointClicked.emit(lat, lon)

    assert ws._map_inspector is not None
    assert ws._map_inspector.isVisible() is True
    assert f"{lat:.2f}" in ws._map_inspector.text_label.text()


def test_a_second_real_click_reuses_the_same_map_inspector_instance(qapp):
    """Real regression guard: never a second, independent popup per click."""
    ws = ACFWorkstation()
    volume = _real_volume()
    ws._on_volume_ready(volume)

    ws.thermodynamics_panel.map_panel.pointClicked.emit(float(volume["lats"][1]), float(volume["lons"][2]))
    first_inspector = ws._map_inspector
    ws.thermodynamics_panel.map_panel.pointClicked.emit(float(volume["lats"][3]), float(volume["lons"][4]))

    assert ws._map_inspector is first_inspector


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
    assert ws.pipeline_monitor.status_snapshot()["Modules"] == "FAIL"


def test_refresh_marks_the_real_ingestion_stage_before_the_solver_run_starts(qapp, monkeypatch):
    """Real Phase 32 regression guard: Ingestion (real model/grid
    validation) completes synchronously and Modules starts RUNNING
    before the real off-thread solver run is even dispatched."""
    ws = ACFWorkstation()
    monkeypatch.setattr("acf.gui.dashboard.acf_workstation.QThreadPool.globalInstance", lambda: _NullThreadPool())

    ws.refresh()

    snapshot = ws.pipeline_monitor.status_snapshot()
    assert snapshot["Ingestion"] == "OK"
    assert snapshot["Modules"] == "RUNNING"


class _NullThreadPool:
    """A real, minimal QThreadPool stand-in that never actually starts
    the worker - keeps this test focused on refresh()'s own synchronous
    pipeline-monitor updates, not the real off-thread run itself
    (already covered by test_refresh_genuinely_runs_a_real_off_thread_volume_run)."""

    def start(self, _worker):
        return None


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
