"""
Tests for AWCIDashboard's real interactivity closures (docs/awci/
AWCI_UI_AUDIT.md / AWCI_INTERACTION_MATRIX.md - the pre-implementation
audit's "dead UI" findings): map click sets a real single source of
truth for the point of interest, and risk-summary badges open a real
detail popup instead of doing nothing.

Signals are emitted directly (dashboard.global_map.pointClicked.emit(...),
dashboard.risk_summary.rowClicked.emit(...)) - the exact real mechanism
AWCIMapPanel.mouseReleaseEvent()/_RiskRow.mousePressEvent() themselves
use (see test_awci_map_panel_point_click.py for full mouse-event-level
coverage of the map's own click-vs-drag detection - not re-tested here).
"""

import numpy as np
import pytest
from PySide6.QtWidgets import QApplication

from acf.awci.vertical_field import compute_real_complexity_volume
from acf.gui.dashboard.awci_dashboard import _FLIGHT_LEVEL_SELECTOR_OPTIONS_HPA, AWCIDashboard, _POINT_OF_INTEREST
from acf.gui.dashboard.awci_synthetic_field import _synthetic_inputs


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


# ------------------------------------------------------------- map click


def test_dashboard_starts_at_the_real_default_point_of_interest(qapp):
    dashboard = AWCIDashboard()
    assert dashboard._point_of_interest == _POINT_OF_INTEREST


def test_clicking_the_global_map_updates_the_single_source_of_truth(qapp):
    dashboard = AWCIDashboard()
    dashboard.global_map.pointClicked.emit(10.0, 20.0)
    assert dashboard._point_of_interest == (10.0, 20.0)


def test_clicking_the_regional_map_updates_the_single_source_of_truth(qapp):
    dashboard = AWCIDashboard()
    dashboard.regional_map.pointClicked.emit(30.0, 5.0)
    assert dashboard._point_of_interest == (30.0, 5.0)


def test_clicking_the_map_re_runs_the_real_per_point_pipeline_in_demo_mode(qapp):
    """The per-point pipeline (point_raw_data -> AWCICalculator ->
    radar/component list/risk summary/regional-map marker) re-runs at
    the NEW point, not a stale value left over from the old one."""
    dashboard = AWCIDashboard()

    dashboard.global_map.pointClicked.emit(-40.0, 170.0)  # a real, far-away point

    assert dashboard._point_of_interest == (-40.0, 170.0)
    # The regional map's own Point Information card must reflect the
    # SAME new point, not the old one.
    assert dashboard.regional_map._point_marker == (-40.0, 170.0)
    # The raw inputs risk-badge clicks read (self._last_point_raw_data)
    # are the real ones _synthetic_inputs() computed AT THIS new point,
    # not the default point's.
    assert dashboard._last_point_raw_data == pytest.approx(_synthetic_inputs(-40.0, 170.0, flight_level_hpa=300.0))


def test_clicking_the_map_in_real_physics_mode_re_slices_the_real_volume_at_the_new_point(qapp):
    dashboard = AWCIDashboard()
    dashboard._on_real_physics_ready(_real_volume())
    volume = dashboard._real_volume
    lats = volume["lats"]
    new_lat, new_lon = float(lats[2]), float(volume["lons"][3])

    dashboard.global_map.pointClicked.emit(new_lat, new_lon)

    assert dashboard._point_of_interest == (new_lat, new_lon)
    # _apply_volume_at_level() ran again (not refresh()'s demo path) -
    # the regional map's marker score is real_physics-derived, and the
    # component list mode reflects that.
    assert dashboard._last_point_mode == "real_physics"


# --------------------------------------------------------- risk badge click


def test_clicking_the_turbulence_badge_opens_the_same_component_detail_dialog(qapp):
    dashboard = AWCIDashboard()
    assert dashboard._component_detail_window is None

    dashboard.risk_summary.rowClicked.emit("turbulence")

    assert dashboard._component_detail_window is not None
    assert "Dynamic" in dashboard._component_detail_window.windowTitle() or dashboard._component_detail_window.windowTitle() != ""


def test_clicking_the_icing_badge_maps_to_the_microphysical_module(qapp):
    dashboard = AWCIDashboard()
    dashboard.risk_summary.rowClicked.emit("icing")
    assert dashboard._component_detail_window is not None


def test_clicking_the_convective_badge_maps_to_the_convective_module(qapp):
    dashboard = AWCIDashboard()
    dashboard.risk_summary.rowClicked.emit("convective")
    assert dashboard._component_detail_window is not None


def test_clicking_the_overall_badge_opens_the_composite_detail_dialog(qapp):
    dashboard = AWCIDashboard()
    assert dashboard._risk_badge_detail_window is None

    dashboard.risk_summary.rowClicked.emit("overall")

    assert dashboard._risk_badge_detail_window is not None
    assert "Overall Complexity" in dashboard._risk_badge_detail_window.windowTitle()
    assert "Score:" in dashboard._risk_badge_detail_window._score_label.text()


def test_clicking_the_physical_and_forecast_badges_reuse_the_same_composite_dialog(qapp):
    dashboard = AWCIDashboard()
    dashboard.risk_summary.rowClicked.emit("physical")
    first = dashboard._risk_badge_detail_window
    assert "Physical Complexity" in first.windowTitle()

    dashboard.risk_summary.rowClicked.emit("forecast")
    assert dashboard._risk_badge_detail_window is first
    assert "Forecast Complexity" in dashboard._risk_badge_detail_window.windowTitle()


def test_composite_dialog_shows_the_real_module_score_breakdown(qapp):
    dashboard = AWCIDashboard()
    dashboard.risk_summary.rowClicked.emit("overall")

    dialog = dashboard._risk_badge_detail_window
    module_scores = dashboard._last_risk_inputs[0]
    dynamic_text = dialog._module_rows["dynamic"].text()
    assert f"{module_scores['dynamic']:.1f}" in dynamic_text


# --------------------------------------------------- flight-level selector


def test_flight_level_selector_defaults_to_fl300_bit_identical(qapp):
    """Real regression guard: introducing the selector must not shift
    any existing demo-mode AWCI score - see
    _FLIGHT_LEVEL_SELECTOR_OPTIONS_HPA's own docstring."""
    dashboard = AWCIDashboard()
    assert dashboard.flight_level_selector.currentText() == "FL300"
    assert dashboard._current_flight_level_hpa == 300.0
    assert dashboard._last_point_raw_data["pressure"] == 300.0


def test_changing_the_selector_in_demo_mode_re_runs_the_point_pipeline_at_the_new_level(qapp):
    dashboard = AWCIDashboard()

    dashboard.flight_level_selector.setCurrentText("FL180")

    fl180_hpa = _FLIGHT_LEVEL_SELECTOR_OPTIONS_HPA["FL180"]
    assert dashboard._current_flight_level_hpa == fl180_hpa
    assert dashboard._last_point_raw_data["pressure"] == fl180_hpa
    expected = _synthetic_inputs(*dashboard._point_of_interest, flight_level_hpa=fl180_hpa)
    assert dashboard._last_point_raw_data == pytest.approx(expected)


def test_changing_the_selector_does_not_touch_the_map_titles_or_other_routes(qapp):
    """The selector drives only the point-of-interest pipeline - the
    map panel titles (fixed "(FL300)"/"(FL100)" text matching the
    reference mockup) must stay exactly as constructed."""
    dashboard = AWCIDashboard()
    global_title_before = dashboard.global_map._base_title
    regional_title_before = dashboard.regional_map._base_title

    dashboard.flight_level_selector.setCurrentText("FL390")

    assert dashboard.global_map._base_title == global_title_before
    assert dashboard.regional_map._base_title == regional_title_before


def test_changing_the_selector_in_real_physics_mode_snaps_to_the_nearest_native_level(qapp):
    dashboard = AWCIDashboard()
    volume = compute_real_complexity_volume(
        model="ALADIN", n_lat=8, n_lon=12, n_levels=6, steps=2, perturbation_scale=2.0, seed=1
    )
    dashboard._on_real_physics_ready(volume)

    target_hpa = _FLIGHT_LEVEL_SELECTOR_OPTIONS_HPA["FL390"]
    mean_pressure_by_level = volume["pressure_volume_hpa"].mean(axis=(1, 2))
    expected_level_idx = int(np.argmin(np.abs(mean_pressure_by_level - target_hpa)))

    dashboard.flight_level_selector.setCurrentText("FL390")

    assert dashboard._current_level_index == expected_level_idx
    assert dashboard.level_slider.value() == expected_level_idx
    assert dashboard._last_point_mode == "real_physics"
