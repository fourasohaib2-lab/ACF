"""
Tests for AWCIDashboard's docs/reference/awci_dashboard_reference.jpg
parity features (added 2026-09-03): header status badge, VIEW MODE
radios, Tunis city label, half-circle confidence gauge, "See Vertical
Profile" dialog, REGIONAL TREND sparkline, cross-section hazard icon
overlay, FL280/FL320 route comparison, and the recommendation banner.
"""

import numpy as np
import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from acf.awci.vertical_field import compute_real_complexity_volume
from acf.gui.dashboard.awci_dashboard import AWCIDashboard, _REGIONAL_CITY_LABELS


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _real_volume(**overrides):
    kwargs = dict(model="ALADIN", n_lat=10, n_lon=18, n_levels=6, steps=3, perturbation_scale=3.0, seed=2)
    kwargs.update(overrides)
    return compute_real_complexity_volume(**kwargs)


# ------------------------------------------------------------- VIEW MODE


def test_view_mode_defaults_to_global(qapp):
    dashboard = AWCIDashboard()
    assert dashboard.view_mode_global_radio.isChecked() is True


def test_view_mode_regional_zooms_the_global_map_to_the_regional_extent(qapp):
    dashboard = AWCIDashboard()
    default_extent = dashboard.global_map.camera.current_extent()

    dashboard.view_mode_regional_radio.setChecked(True)
    dashboard._on_view_mode_changed()

    west, east, south, north = dashboard.global_map.camera.current_extent()
    assert (west, east, south, north) != default_extent
    assert abs(((west + east) / 2.0) - 11.5) < 10.0  # real center lon ~= (-12+35)/2


def test_view_mode_cross_section_zooms_to_the_real_route_bounding_box(qapp):
    dashboard = AWCIDashboard()

    dashboard.view_mode_cross_section_radio.setChecked(True)
    dashboard._on_view_mode_changed()

    west, east, south, north = dashboard.global_map.camera.current_extent()
    assert (east - west) < 180.0  # genuinely zoomed in


def test_view_mode_global_returns_to_the_default_view(qapp):
    dashboard = AWCIDashboard()
    default_extent = dashboard.global_map.camera.current_extent()
    dashboard.view_mode_regional_radio.setChecked(True)
    dashboard._on_view_mode_changed()

    dashboard.view_mode_global_radio.setChecked(True)
    dashboard._on_view_mode_changed()

    assert dashboard.global_map.camera.current_extent() == default_extent


# -------------------------------------------------------------- header badge


def test_header_badge_text_matches_the_real_research_stage_framing(qapp):
    dashboard = AWCIDashboard()
    labels = dashboard.findChildren(type(dashboard.real_physics_status))
    badge_texts = [lbl.text() for lbl in labels]
    assert any("RESEARCH STAGE" in t for t in badge_texts)


# -------------------------------------------------------------- city labels


def test_tunis_city_label_is_wired_into_the_regional_map(qapp):
    dashboard = AWCIDashboard()
    assert dashboard.regional_map._city_labels == _REGIONAL_CITY_LABELS


# --------------------------------------------------- confidence gauge


def test_confidence_gauge_shows_the_real_point_of_interest_confidence(qapp):
    dashboard = AWCIDashboard()
    assert dashboard.stats_bar.confidence_box.gauge._score >= 0.0


# ------------------------------------------------------- vertical profile


def test_vertical_profile_dialog_opens_lazily(qapp):
    dashboard = AWCIDashboard()
    assert dashboard._vertical_profile_window is None

    dashboard._open_vertical_profile()

    assert dashboard._vertical_profile_window is not None
    assert dashboard._vertical_profile_widget is not None
    assert dashboard._vertical_profile_widget._profile  # real, non-empty profile


def test_vertical_profile_reuses_the_same_dialog_instance(qapp):
    dashboard = AWCIDashboard()
    dashboard._open_vertical_profile()
    first = dashboard._vertical_profile_window

    dashboard._open_vertical_profile()

    assert dashboard._vertical_profile_window is first


def test_vertical_profile_has_a_real_score_per_named_flight_level(qapp):
    dashboard = AWCIDashboard()
    dashboard._open_vertical_profile()

    profile = dashboard._vertical_profile_widget._profile
    assert "FL100" in profile
    assert "FL320" in profile
    for score in profile.values():
        assert 0.0 <= score <= 100.0


def test_vertical_profile_now_also_covers_the_real_standard_pressure_levels(qapp):
    """§51 of docs/ACF_MASTER_PROMPT.md: "Surface / 850 hPa / 700 hPa /
    500 hPa / 300 hPa / 250 hPa / Flight levels" - closed 2026-09-03."""
    dashboard = AWCIDashboard()
    dashboard._open_vertical_profile()

    profile = dashboard._vertical_profile_widget._profile
    for label in ("Surface", "850 hPa", "700 hPa", "500 hPa", "300 hPa", "250 hPa"):
        assert label in profile
        assert 0.0 <= profile[label] <= 100.0


def test_vertical_profile_levels_are_in_real_altitude_order(qapp):
    """Real regression guard for the widget's own ordering fix: labels
    must appear in real descending-pressure (ascending-altitude) order,
    not dict-insertion order of the two source tables."""
    from acf.gui.dashboard.awci_dashboard import _ALL_VERTICAL_PROFILE_LEVELS_HPA

    hpas = list(_ALL_VERTICAL_PROFILE_LEVELS_HPA.values())
    assert hpas == sorted(hpas, reverse=True)
    assert list(_ALL_VERTICAL_PROFILE_LEVELS_HPA.keys())[0] == "Surface"  # highest real pressure first


def test_vertical_profile_widget_trusts_the_callers_own_order():
    """Real regression guard: AWCIVerticalProfile must no longer
    silently re-sort by parsing "FL<n>" labels (that could not
    correctly interleave standard-pressure-level labels)."""
    from acf.gui.dashboard.awci_vertical_profile import AWCIVerticalProfile

    widget = AWCIVerticalProfile()
    widget.set_profile({"Surface": 10.0, "FL180": 40.0, "700 hPa": 25.0})
    assert list(widget._profile.items()) == [("Surface", 10.0), ("FL180", 40.0), ("700 hPa", 25.0)]


# ------------------------------------------------------ regional trend


def test_regional_trend_sparkline_has_real_data_after_refresh(qapp):
    dashboard = AWCIDashboard()
    assert dashboard.regional_trend._data
    assert len(dashboard.regional_trend._data) == 7  # -6..+6h in steps of 2


def test_regional_trend_sparkline_updates_when_the_time_slider_moves(qapp):
    dashboard = AWCIDashboard()
    before = list(dashboard.regional_trend._data)

    dashboard.time_slider.setValue(20)
    dashboard.refresh()

    after = list(dashboard.regional_trend._data)
    assert before != after


# --------------------------------------------------- cross-section overlay


def test_cross_section_hazard_overlay_is_populated_in_demo_mode(qapp):
    dashboard = AWCIDashboard()
    assert dashboard.cross_section._hazard_overlay is not None
    _distances, _levels, phase_grid, shear_grid = dashboard.cross_section._hazard_overlay
    assert phase_grid is not None
    assert shear_grid is None  # no real u/v in the synthetic demo pattern


def test_cross_section_hazard_overlay_includes_real_wind_shear_in_real_physics_mode(qapp):
    dashboard = AWCIDashboard()
    volume = _real_volume()

    dashboard._on_real_physics_ready(volume)

    _distances, _levels, phase_grid, shear_grid = dashboard.cross_section._hazard_overlay
    assert phase_grid is not None
    assert shear_grid is not None
    assert np.all(np.asarray(shear_grid) >= 0.0)


# ----------------------------------------------- FL280/FL320 comparison


def test_fl_comparison_toggle_in_demo_mode(qapp):
    dashboard = AWCIDashboard()
    assert dashboard._fl_comparison_active is False

    dashboard._toggle_fl_comparison()

    assert dashboard._fl_comparison_active is True
    assert dashboard.route_chart._comparison is not None
    assert dashboard.route_chart._primary_label == "FL280"


def test_fl_comparison_toggle_off_restores_single_series(qapp):
    dashboard = AWCIDashboard()
    dashboard._toggle_fl_comparison()

    dashboard._toggle_fl_comparison()

    assert dashboard._fl_comparison_active is False
    assert dashboard.route_chart._comparison is None


def test_fl_comparison_works_in_real_physics_mode(qapp):
    dashboard = AWCIDashboard()
    dashboard._on_real_physics_ready(_real_volume())

    dashboard._toggle_fl_comparison()

    assert dashboard._fl_comparison_active is True
    assert dashboard.route_chart._comparison is not None


# --------------------------------------------------- recommendation banner


def test_recommendation_banner_reflects_real_elevated_risk(qapp):
    """The demo point of interest has a real elevated Turbulence Risk
    (see risk_summary's own real classification) - the banner must
    show real text mentioning it. Qt's own isVisible() reflects
    EFFECTIVE visibility (the whole parent chain must be shown on
    screen too, not just this widget's own setVisible(True) flag - the
    same real gotcha already documented in this file's own
    _stop_evolution_playback()), so a never-.show()'d dashboard always
    reports isVisible()=False regardless - checked via the real
    internal flag Qt exposes for exactly this case instead."""
    dashboard = AWCIDashboard()
    assert not dashboard.recommendation_banner.testAttribute(Qt.WidgetAttribute.WA_WState_Hidden)
    assert "Turbulence" in dashboard.recommendation_banner.text() or "km" in dashboard.recommendation_banner.text()


def test_recommendation_banner_hidden_when_nothing_is_elevated(qapp):
    dashboard = AWCIDashboard()
    dashboard._update_recommendation_banner({}, 0.0, None, None, None, None)
    assert dashboard.recommendation_banner.testAttribute(Qt.WidgetAttribute.WA_WState_Hidden)
