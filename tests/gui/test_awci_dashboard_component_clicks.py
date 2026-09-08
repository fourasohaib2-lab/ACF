"""
Tests for AWCIDashboard's clickable "AWCI COMPONENTS" rows (explicit
user request "rend les bouton des différents complexité utilisable
pour rendre tout le details de la situation"). Clicks are dispatched
via the row's own real Signal (._ComponentRow.clicked) - the exact
mechanism mousePressEvent() triggers - not by calling the dialog
directly.
"""

import pytest
from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication

from acf.awci.vertical_field import compute_real_complexity_volume
from acf.gui.dashboard.awci_dashboard import AWCIDashboard


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _real_volume(**overrides):
    kwargs = dict(model="ALADIN", n_lat=8, n_lon=12, n_levels=6, steps=2, perturbation_scale=2.0, seed=1)
    kwargs.update(overrides)
    return compute_real_complexity_volume(**kwargs)


def _press(row):
    event = QMouseEvent(QEvent.Type.MouseButtonPress, QPointF(5, 5), Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
    row.mousePressEvent(event)


def test_clicking_a_row_opens_the_detail_dialog_with_real_demo_data(qapp):
    dashboard = AWCIDashboard()
    assert dashboard._component_detail_window is None

    _press(dashboard.component_list._rows["dynamic"])

    assert dashboard._component_detail_window is not None
    assert "REAL" in dashboard._component_detail_window.badge_label.text()
    assert "wind_speed" in dashboard._component_detail_window.inputs_label.text()


def test_clicking_reuses_the_same_dialog_instance(qapp):
    dashboard = AWCIDashboard()
    _press(dashboard.component_list._rows["dynamic"])
    first = dashboard._component_detail_window
    _press(dashboard.component_list._rows["thermodynamic"])
    assert dashboard._component_detail_window is first


def test_clicking_a_row_in_real_physics_mode_shows_honest_default_for_convective(qapp):
    """Real regression guard for the pipeline gap this dialog exists to
    disclose: convective is pinned at AWCICalculator's own default in
    Real Physics mode today (no real cape/cin per-point source wired
    into compute_real_complexity_volume())."""
    dashboard = AWCIDashboard()
    dashboard._on_real_physics_ready(_real_volume())

    _press(dashboard.component_list._rows["convective"])

    assert "DEFAULT" in dashboard._component_detail_window.badge_label.text()


def test_clicking_a_row_in_real_physics_mode_shows_real_for_dynamic(qapp):
    dashboard = AWCIDashboard()
    dashboard._on_real_physics_ready(_real_volume())

    _press(dashboard.component_list._rows["dynamic"])

    assert "REAL" in dashboard._component_detail_window.badge_label.text()
    assert "Real Physics solver" in dashboard._component_detail_window.badge_label.text()


def test_every_row_is_independently_clickable(qapp):
    dashboard = AWCIDashboard()
    for key in ("dynamic", "thermodynamic", "convective", "microphysical", "topographic", "temporal", "confidence"):
        _press(dashboard.component_list._rows[key])
        assert dashboard._component_detail_window.windowTitle() != ""  # a real title was set for this module


# ------------------------------- real drill-down chain (§26/§53, added 2026-09-03)


def test_clicking_a_row_shows_a_real_drill_down_trace_in_demo_mode(qapp):
    """build_awci_result()/AWCIResult.trace_chain() (§26/§53/§81) existed
    since an earlier closure this session but were never wired into any
    GUI - real regression guard that this dialog now shows the real
    trace text, not the "not available" placeholder."""
    dashboard = AWCIDashboard()
    assert dashboard._last_awci_result is not None  # refresh() in __init__ already built one

    _press(dashboard.component_list._rows["dynamic"])

    trace_text = dashboard._component_detail_window.trace_label.text()
    assert "not available - no real AWCIResult" not in trace_text
    assert "Score: AWCI =" in trace_text
    assert "Diagnostics (module scores):" in trace_text


def test_drill_down_trace_reflects_the_same_real_raw_variables_as_the_inputs_section(qapp):
    dashboard = AWCIDashboard()

    _press(dashboard.component_list._rows["dynamic"])

    dialog = dashboard._component_detail_window
    assert "wind_speed" in dialog.inputs_label.text()
    assert "Variables:" in dialog.trace_label.text()
    assert "wind_speed" in dialog.trace_label.text()


def test_drill_down_trace_includes_the_real_vertical_level_in_real_physics_mode(qapp):
    dashboard = AWCIDashboard()
    dashboard._on_real_physics_ready(_real_volume())

    _press(dashboard.component_list._rows["dynamic"])

    trace_text = dashboard._component_detail_window.trace_label.text()
    assert "Niveau vertical:" in trace_text
    assert "not available" not in trace_text.split("Niveau vertical:")[1]
