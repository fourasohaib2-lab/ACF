"""
Tests for ACFGeneralDashboard (src/acf/gui/dashboard/acf_general_dashboard.py)
- the general, multi-lead-time ACF research dashboard, explicit user
request "vasy respecte le prompt" (docs/ACF_MASTER_PROMPT.md sections
27-29), matching docs/reference/acf_dashboard_reference.jpg.

qtbot.waitUntil() drives the real off-thread QThreadPool worker path
end-to-end for refresh()/consensus (same discipline as
tests/test_esoc_awci_field.py - a bare-lambda signal connection bug
would only be caught by actually running the worker, not by calling its
run() synchronously), while the lead-time-tab-reslice and gauge/radar
correctness checks call _on_evolution_ready()/_on_consensus_ready()
directly with a small real precomputed result (same convention as
tests/gui/test_awci_dashboard_evolution.py) for speed and determinism.
"""

from __future__ import annotations

import numpy as np
import pytest
from PySide6.QtWidgets import QApplication

from acf.awci.calculator import AWCICalculator
from acf.awci.temporal_field import compute_real_complexity_evolution
from acf.gui.dashboard.acf_general_dashboard import ACFGeneralDashboard, _POINT_OF_INTEREST


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _real_evolution(**overrides):
    kwargs = dict(model="ALADIN", n_lat=8, n_lon=14, n_levels=4, n_frames=3, steps_per_frame=2, perturbation_scale=2.0, seed=1)
    kwargs.update(overrides)
    return compute_real_complexity_evolution(**kwargs)


def test_starts_inert_no_auto_computation(qapp):
    """Construction alone must not start a real background computation -
    see ACFGeneralDashboard.__init__'s own docstring note."""
    dashboard = ACFGeneralDashboard()
    assert dashboard._evolution is None
    assert dashboard.status()["has_evolution"] is False
    assert "not yet computed" in dashboard.status_label.text().lower()


def test_refresh_genuinely_runs_a_real_off_thread_evolution(qtbot):
    """Drives the actual QThreadPool.globalInstance().start() + Qt event
    loop path, not a direct call - the same class of bug this session
    already found once (a bare-lambda signal connection PySide6 Auto
    connection silently never fires) would only be caught this way."""
    dashboard = ACFGeneralDashboard()
    qtbot.addWidget(dashboard)

    dashboard.refresh()

    qtbot.waitUntil(lambda: dashboard._evolution is not None, timeout=60000)
    assert dashboard.map_panel._external_field is not None
    assert dashboard.cross_section is not None
    assert "✅" in dashboard.status_label.text()


def test_on_evolution_ready_renders_frame_zero_and_enables_tabs(qapp):
    dashboard = ACFGeneralDashboard()
    evolution = _real_evolution()

    dashboard._on_evolution_ready(evolution)

    assert dashboard._evolution is evolution
    assert dashboard._current_frame_index == 0
    assert dashboard.lead_time_buttons[0].isChecked() is True
    lons, lats, grid = dashboard.map_panel._external_field
    np.testing.assert_array_equal(grid, evolution["awci_evolution"][0, 0])


def test_lead_time_button_labels_are_the_real_valid_times_not_fabricated_text(qapp):
    """Regression test: an earlier version of this dashboard hard-coded
    "T+0h/T+3h/T+6h/T+12h/T+24h" button text - real
    compute_real_complexity_evolution() frames are spaced UNIFORMLY, so
    that fixed uneven-spacing text could never match what was actually
    computed. Labels must come from the real valid_time_seconds."""
    dashboard = ACFGeneralDashboard()
    evolution = _real_evolution(n_frames=5)

    dashboard._on_evolution_ready(evolution)

    for i, btn in enumerate(dashboard.lead_time_buttons):
        expected_h = evolution["valid_time_seconds"][i] / 3600.0
        assert btn.text() == f"T+{expected_h:.2f}h"
        # isHidden() reflects this widget's own explicit flag, unlike
        # isVisible() which also requires the whole parent chain to be
        # shown on screen (not the case for a bare, unshown dashboard).
        assert btn.isHidden() is False


def test_evolution_with_fewer_frames_than_buttons_hides_the_extra_buttons(qapp):
    """compute_real_complexity_evolution(n_frames=...) can return fewer
    real frames than this dashboard's fixed button count - the extra
    buttons must hide rather than crash or show stale/fabricated text."""
    dashboard = ACFGeneralDashboard()
    evolution = _real_evolution(n_frames=3)

    dashboard._on_evolution_ready(evolution)

    for i, btn in enumerate(dashboard.lead_time_buttons):
        assert btn.isHidden() is (i >= 3)


def test_lead_time_tab_click_reslices_without_recomputing(qapp):
    dashboard = ACFGeneralDashboard()
    evolution = _real_evolution(n_frames=3)
    dashboard._on_evolution_ready(evolution)

    dashboard._on_lead_time_clicked(2)

    assert dashboard._evolution is evolution  # same object - no new solver run
    assert dashboard._current_frame_index == 2
    assert dashboard.lead_time_buttons[2].isChecked() is True
    assert dashboard.lead_time_buttons[0].isChecked() is False
    lons, lats, grid = dashboard.map_panel._external_field
    np.testing.assert_array_equal(grid, evolution["awci_evolution"][2, 0])


def test_gauge_and_radar_match_an_independent_awcicalculator_call(qapp):
    from acf.gui.dashboard.awci_radar import _AXES

    dashboard = ACFGeneralDashboard()
    evolution = _real_evolution()
    dashboard._on_evolution_ready(evolution)

    lats, lons = evolution["lats"], evolution["lons"]
    lat_idx = int(np.argmin(np.abs(np.asarray(lats) - _POINT_OF_INTEREST[0])))
    lon_idx = int(np.argmin(np.abs(np.asarray(lons) - _POINT_OF_INTEREST[1])))
    point_data = {
        "temperature": float(evolution["temperature_evolution"][0, 0, lat_idx, lon_idx]),
        "wind_speed": float(evolution["wind_speed_evolution"][0, 0, lat_idx, lon_idx]),
        "specific_humidity": float(evolution["specific_humidity_evolution"][0, 0, lat_idx, lon_idx]),
        "pressure": float(evolution["pressure_evolution_hpa"][0, 0, lat_idx, lon_idx]),
    }
    expected = AWCICalculator().calculate(point_data)

    assert dashboard.complexity_gauge._score == pytest.approx(expected["awci"], abs=0.05)

    # Radar stores no public data attribute - it is a pure matplotlib
    # widget - so read back the actual plotted polar line values and
    # compare against the same real module_scores dict, in the same
    # axis order the widget itself uses (acf.gui.dashboard.awci_radar._AXES).
    expected_values = [expected["module_scores"].get(key, 0.0) for key, _ in _AXES]
    expected_values_closed = expected_values + expected_values[:1]
    plotted_line = dashboard.radar.axis.get_lines()[0]
    np.testing.assert_allclose(plotted_line.get_ydata(), expected_values_closed)


def test_lead_time_click_before_any_evolution_is_a_safe_no_op(qapp):
    dashboard = ACFGeneralDashboard()
    dashboard._on_lead_time_clicked(3)  # no evolution ready yet
    assert dashboard._evolution is None
    assert dashboard._current_frame_index == 0


def test_hamburger_menu_matches_the_reference_mockups_own_icon(qapp):
    """docs/reference/acf_dashboard_reference.jpg shows a real "☰" icon
    top-left - explicit user instruction (2026-09-04): real dashboard
    actions belong behind it, not as extra inline widgets in the fixed
    panels below."""
    dashboard = ACFGeneralDashboard()
    assert dashboard.menu_button.text() == "☰"
    assert [a.text() for a in dashboard.nav_menu.actions()] == ["🔄 Refresh Evolution", "🔄 Compute Consensus"]


def test_triggering_the_real_refresh_menu_action_runs_the_real_refresh(qapp, monkeypatch):
    """Real proof the menu action is wired to the exact same real
    method the old inline QPushButton called - not a decorative
    QAction with no real connection."""
    dashboard = ACFGeneralDashboard()
    called = []
    monkeypatch.setattr(dashboard, "refresh", lambda: called.append(True))

    dashboard.refresh_button.trigger()

    assert called == [True]


def test_triggering_the_real_consensus_menu_action_runs_the_real_consensus(qapp, monkeypatch):
    dashboard = ACFGeneralDashboard()
    called = []
    monkeypatch.setattr(dashboard, "_start_consensus", lambda: called.append(True))

    dashboard.consensus_button.trigger()

    assert called == [True]


def test_evolution_failure_reports_error_and_reenables_refresh(qapp):
    dashboard = ACFGeneralDashboard()
    dashboard.refresh_button.setEnabled(False)

    dashboard._on_evolution_failed("boom")

    assert dashboard.refresh_button.isEnabled() is True
    assert "failed" in dashboard.status_label.text().lower()


def test_consensus_button_genuinely_runs_off_thread(qtbot):
    """Same off-thread discipline as test_refresh_genuinely_runs_a_real_off_thread_evolution."""
    dashboard = ACFGeneralDashboard()
    qtbot.addWidget(dashboard)
    dashboard._on_evolution_ready(_real_evolution())

    dashboard._start_consensus()

    qtbot.waitUntil(lambda: "consensus computed" in dashboard.status_label.text().lower(), timeout=60000)
    assert dashboard.consensus_button.isEnabled() is True
    assert dashboard.spread_chart.axis.patches  # real bars drawn


def test_consensus_failure_reports_error_and_reenables_button(qapp):
    dashboard = ACFGeneralDashboard()
    dashboard.consensus_button.setEnabled(False)

    dashboard._on_consensus_failed("boom")

    assert dashboard.consensus_button.isEnabled() is True
    assert "failed" in dashboard.status_label.text().lower()


def test_on_consensus_ready_updates_uncertainty_gauge_from_the_real_normalizer(qapp):
    from acf.awci.normalizer import Normalizer

    dashboard = ACFGeneralDashboard()
    per_model_value = {"ARPEGE": 290.0, "ALADIN": 292.0}
    result = {"per_model_value": per_model_value, "disagreement_mean": 291.0, "disagreement_spread": 1.0}

    dashboard._on_consensus_ready(result)

    expected = Normalizer.normalize_model_disagreement(1.0, "temperature") * 100.0
    assert dashboard.uncertainty_gauge._score == pytest.approx(expected, abs=0.05)
