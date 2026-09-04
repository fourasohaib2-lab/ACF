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
    assert len(pm.list_panel_names()) == 29
    assert pm.get_panel("earth_monitoring") is not None
    assert pm.get_panel("simulation") is not None
    assert pm.get_panel("awci_dashboard") is not None
    assert pm.get_panel("catalog") is not None


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


def test_esoc_left_sidebar_without_a_registry_has_no_fabricated_status_line(qapp):
    sidebar = ESOCLeftSidebar()
    assert sidebar.status_label.testAttribute(Qt.WidgetAttribute.WA_WState_Hidden)


def test_esoc_left_sidebar_shows_the_real_connectivity_status(qapp):
    """Closes the last gap disclosed in ESOCLeftSidebar's own NOTE
    (correction, 2026-09-04): get_system_status_summary() also had no
    real GUI consumer anywhere before this."""
    registry = ModuleRegistry()
    sidebar = ESOCLeftSidebar(registry=registry)

    assert not sidebar.status_label.testAttribute(Qt.WidgetAttribute.WA_WState_Hidden)
    expected = registry.get_system_status_summary()
    assert f"{expected['connected_count']}/{expected['total_modules']}" in sidebar.status_label.text()


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


# ------------------------------------------ System Explorer tree -> real panel


def test_clicking_a_real_leaf_with_a_verified_panel_switches_to_it(qapp):
    """Closes a real, confirmed "dead click" bug: ESOCLeftSidebar's
    own on_select_callback was connected to a real tree.itemClicked
    signal but never supplied by any real caller - every one of the
    tree's ~150 leaves was a genuine no-op. ESOCLayout is its first
    real caller."""
    window = ESOCWindow()
    layout = window.layout_manager

    layout._on_sidebar_item_selected("Ocean", "Earth System")

    ocean_panel = layout.panel_manager.get_panel("ocean")
    assert layout.bottom_tabs.currentWidget() is ocean_panel


def test_clicking_a_real_hpc_leaf_switches_to_its_distinct_real_panel(qapp):
    """The "HPC" category has several distinct real panels among its
    own leaves (unlike e.g. "Simulation", which has exactly one) -
    each leaf must resolve to its own, not a shared category-wide
    one."""
    window = ESOCWindow()
    layout = window.layout_manager

    layout._on_sidebar_item_selected("Job Explorer", "HPC")
    assert layout.bottom_tabs.currentWidget() is layout.panel_manager.get_panel("job_explorer")

    layout._on_sidebar_item_selected("CUDA GPU Monitor", "HPC")
    assert layout.bottom_tabs.currentWidget() is layout.panel_manager.get_panel("gpu_monitor")


def test_clicking_a_category_header_opens_its_one_real_panel(qapp):
    """A category with exactly one real panel across all its leaves -
    clicking the category header itself (category=None, no parent)
    must also resolve, the same as clicking any of its leaves would
    via the fallback path below."""
    window = ESOCWindow()
    layout = window.layout_manager

    layout._on_sidebar_item_selected("Simulation", None)

    assert layout.bottom_tabs.currentWidget() is layout.panel_manager.get_panel("simulation")


def test_clicking_the_catalog_category_opens_the_real_catalog_panel(qapp):
    """Real regression guard (2026-09-04): "Catalog" used to be a
    genuinely unmapped category - all 3 of its leaves (WMO Standards,
    CF-1.8 Conventions, ECMWF Parameters) were honest no-ops. Now real
    and wired, same category-level-fallback convention as Simulation."""
    window = ESOCWindow()
    layout = window.layout_manager

    layout._on_sidebar_item_selected("Catalog", None)
    assert layout.bottom_tabs.currentWidget() is layout.panel_manager.get_panel("catalog")

    layout._on_sidebar_item_selected("WMO Standards", "Catalog")
    assert layout.bottom_tabs.currentWidget() is layout.panel_manager.get_panel("catalog")


def test_clicking_an_unmapped_leaf_under_a_single_panel_category_falls_back_to_it(qapp):
    """"AMR" itself has no specific real panel, but its parent
    category "Simulation" does - real category-level fallback."""
    window = ESOCWindow()
    layout = window.layout_manager

    layout._on_sidebar_item_selected("AMR", "Simulation")

    assert layout.bottom_tabs.currentWidget() is layout.panel_manager.get_panel("simulation")


def test_clicking_a_genuinely_unmapped_label_is_an_honest_no_op(qapp):
    """"Atmosphere" (Earth System) has no real panel anywhere - must
    stay a real no-op, never a guessed/wrong navigation."""
    window = ESOCWindow()
    layout = window.layout_manager
    layout.bottom_tabs.setCurrentIndex(0)
    before = layout.bottom_tabs.currentIndex()

    layout._on_sidebar_item_selected("Atmosphere", "Earth System")

    assert layout.bottom_tabs.currentIndex() == before


def test_a_real_qt_tree_click_reaches_the_real_panel_switch(qapp):
    """End-to-end: a real tree.itemClicked signal, not a direct method
    call - the same discipline as AWCI's own
    test_clicking_a_real_bar_via_a_real_mouse_event_opens_the_dialog."""
    from PySide6.QtWidgets import QTreeWidgetItemIterator

    window = ESOCWindow()
    layout = window.layout_manager
    sidebar = layout.left_sidebar

    it = QTreeWidgetItemIterator(sidebar.tree)
    ocean_item = None
    while it.value():
        if it.value().text(0) == "Ocean":
            ocean_item = it.value()
            break
        it += 1
    assert ocean_item is not None

    sidebar.tree.itemClicked.emit(ocean_item, 0)

    assert layout.bottom_tabs.currentWidget() is layout.panel_manager.get_panel("ocean")


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
