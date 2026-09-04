"""Unit test suite for ACF-UI-011 Unified Earth System Operations Center (ESOC)."""

import os
import tempfile

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from acf.gui.esoc.command_dispatcher import CommandDispatcher
from acf.gui.esoc.esoc_sidebar import ESOCLeftSidebar, ESOCRightSidebar
from acf.gui.esoc.esoc_statusbar import ESOCStatusBar
from acf.gui.esoc.esoc_toolbar import ESOCToolbar
from acf.gui.esoc.esoc_window import ESOCWindow
from acf.gui.esoc.esoc_workspace import WorkspaceManager, WorkspaceMode
from acf.gui.esoc.module_registry import ModuleRegistry
from acf.gui.esoc.panel_manager import PanelManager
from acf.gui.esoc.session_manager import SessionManager
from acf.gui.esoc.view_manager import ViewManager


@pytest.fixture(scope="session")
def qapp():
    """Ensure a PySide6 QApplication instance exists for Qt widget tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_module_registry():
    registry = ModuleRegistry()
    assert len(registry.list_modules()) >= 15
    assert registry.is_connected("coupled_earth_solver")
    assert registry.is_connected("atmospheric_model")
    assert registry.is_connected("ocean_model")
    assert registry.is_connected("neural_operator")
    status = registry.get_system_status_summary()
    assert status["total_modules"] >= 15
    results = registry.global_search("temperature")
    assert len(results) > 0


def test_command_dispatcher():
    dispatcher = CommandDispatcher()
    executed = []

    def sample_handler(val: int):
        executed.append(val)
        return {"val": val}

    dispatcher.register_command("test_cmd", sample_handler)
    res = dispatcher.dispatch("test_cmd", val=42)
    assert res == {"val": 42}
    assert executed == [42]


def test_session_manager():
    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = os.path.join(tmpdir, "session.json")
        sm = SessionManager(session_filepath=json_path)
        assert sm.save_session({"workspace_mode": "Climate"}) is True
        assert os.path.exists(json_path)
        data = sm.load_session()
        assert data["workspace_mode"] == "Climate"


def test_workspace_manager():
    wm = WorkspaceManager(WorkspaceMode.METEOROLOGIST)
    modes = wm.list_modes()
    assert len(modes) == 10
    profile = wm.set_mode(WorkspaceMode.CLIMATE)
    assert profile["mode_name"] == "Climate"
    assert "climate" in profile["visible_panels"]


def test_panel_manager(qapp):
    registry = ModuleRegistry()
    dispatcher = CommandDispatcher()
    pm = PanelManager(registry, dispatcher)
    assert len(pm.list_panel_names()) == 28
    assert pm.get_panel("earth_monitoring") is not None
    assert pm.get_panel("simulation") is not None
    assert pm.get_panel("awci_dashboard") is not None


def test_view_manager(qapp):
    vm = ViewManager()
    assert "Satellite RGB" in vm.active_layers
    new_layers = vm.toggle_layer("Satellite RGB")
    assert "Satellite RGB" not in new_layers


def test_esoc_widgets(qapp):
    sb_left = ESOCLeftSidebar()
    sb_right = ESOCRightSidebar()
    tb = ESOCToolbar()
    st = ESOCStatusBar()

    assert sb_left is not None
    assert sb_right is not None
    assert tb is not None
    assert st is not None

    st.update_metrics(utc_str="2026-08-03 08:00:00Z", workspace_mode="Climate")
    assert "Climate" in st.lbl_workspace.text()


def test_esoc_left_sidebar_without_a_registry_has_no_fabricated_search_results(qapp):
    """Real, backward-compatible default (registry=None, e.g. this
    widget used standalone as test_esoc_widgets does above) - a real
    query must never show a made-up results line with no registry
    behind it."""
    sidebar = ESOCLeftSidebar()
    sidebar.search_input.setText("temperature")
    assert sidebar.search_results_label.testAttribute(Qt.WidgetAttribute.WA_WState_Hidden)


def test_esoc_left_sidebar_search_uses_the_real_module_registry(qapp):
    """Closes the gap disclosed in ESOCLeftSidebar's own NOTE
    (correction, 2026-09-04): the "🔍 Universal Search" placeholder
    previously had no way to reach ModuleRegistry.global_search() at
    all - this is that search bar's first real backend."""
    registry = ModuleRegistry()
    sidebar = ESOCLeftSidebar(registry=registry)

    sidebar.search_input.setText("temperature")

    assert not sidebar.search_results_label.testAttribute(Qt.WidgetAttribute.WA_WState_Hidden)
    expected = registry.global_search("temperature")
    assert f"{len(expected)} real match" in sidebar.search_results_label.text()
    assert expected  # a real, non-empty result for this query - the label's own count is meaningful


def test_esoc_left_sidebar_search_honestly_reports_zero_real_matches(qapp):
    registry = ModuleRegistry()
    sidebar = ESOCLeftSidebar(registry=registry)

    sidebar.search_input.setText("xyznonexistentquery123")

    assert "0 real matches" in sidebar.search_results_label.text()


def test_esoc_left_sidebar_search_results_hide_when_the_query_is_cleared(qapp):
    registry = ModuleRegistry()
    sidebar = ESOCLeftSidebar(registry=registry)
    sidebar.search_input.setText("catalog")
    assert not sidebar.search_results_label.testAttribute(Qt.WidgetAttribute.WA_WState_Hidden)

    sidebar.search_input.setText("")

    assert sidebar.search_results_label.testAttribute(Qt.WidgetAttribute.WA_WState_Hidden)


def test_esoc_layout_passes_the_real_registry_through_to_the_search_bar(qapp):
    """End-to-end wiring proof: ESOCWindow's own real ModuleRegistry
    reaches ESOCLeftSidebar through ESOCLayout - not a second/
    independent instance."""
    window = ESOCWindow()
    assert window.layout_manager.left_sidebar.registry is window.registry


def test_esoc_right_sidebar_discloses_illustrative_content(qapp):
    """
    CORRECTED: ESOCRightSidebar's 7 inspector tabs used to present
    fixed values (a selected grid cell's temperature/wind, CAPE/CIN
    diagnostics, a corrupted "SHA256 checksum", a fake running
    forecast log, GPU/TFLOPS performance numbers) as if live, with no
    real selection/dataset/simulation/HPC feed connected. Clicking
    "Render Plot" also used to unconditionally claim a plot was
    generated with no plot ever actually produced. See
    esoc_sidebar.py's own NOTE (correction).
    """
    sb_right = ESOCRightSidebar()

    for tab in (
        sb_right.tab_props,
        sb_right.tab_diag,
        sb_right.tab_meta,
        sb_right.tab_sim,
        sb_right.tab_logs,
        sb_right.tab_perf,
    ):
        assert "Example Layout" in tab.toPlainText()

    sb_right._render_plot()
    assert "[NOT IMPLEMENTED]" in sb_right.txt_ai.toPlainText()
    assert "generated successfully" not in sb_right.txt_ai.toPlainText()


def test_esoc_controller_and_window(qapp):
    window = ESOCWindow()
    meta = ESOCWindow.get_esoc_metadata()
    assert meta["platform_name"] == "Unified Earth System Operations Center (ESOC)"
    assert meta["operational_modes"] == 10
    assert meta["dock_panels"] == 11

    # Test controller handler executions
    res_sim = window.controller.handle_run_simulation(dt=10.0)
    assert res_sim["status"] == "SUCCESS"

    # CORRECTED: handle_run_assimilation() used to claim "SUCCESS" for
    # any scheme with no real DA engine connected.
    res_da = window.controller.handle_run_assimilation("4D-Var")
    assert res_da["status"] == "NOT_EXECUTED_NO_DA_ENGINE_CONNECTED"

    res_ai = window.controller.handle_run_ai_forecast()
    assert res_ai["status"] == "SUCCESS"

    # CORRECTED: handle_assess_hazards() used to unconditionally emit
    # a fabricated "Tropical Cyclone Cat 3" hazard alert signal and
    # claim "SUCCESS" - operationally dangerous false-alarm risk, no
    # longer emits any alert.
    res_haz = window.controller.handle_assess_hazards()
    assert res_haz["status"] == "NOT_ASSESSED_NO_HAZARD_DETECTION_ENGINE_CONNECTED"
    assert res_haz["hazards_assessed"] is False
