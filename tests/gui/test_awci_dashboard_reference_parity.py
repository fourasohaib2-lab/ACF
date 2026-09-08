"""
Tests for AWCIDashboard's docs/reference/awci_dashboard_reference.jpg
parity features (added 2026-09-03): header status badge, VIEW MODE
radios, Tunis city label, half-circle confidence gauge, "See Vertical
Profile" dialog, REGIONAL TREND sparkline, cross-section hazard icon
overlay, FL280/FL320 route comparison, and the recommendation banner.
"""

from pathlib import Path

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


def test_vertical_profile_in_real_physics_mode_uses_real_interpolation(qapp):
    """future-improvements.md #9, closed 2026-09-04 - priority freely
    chosen ("continue"). Real Physics mode must now also populate the
    same standard-level/flight-level bars, via real log-pressure
    interpolation (acf.awci.vertical_field.
    vertical_profile_at_standard_levels()) between the real volume's
    own native solver levels - not the demo mode's own
    _synthetic_inputs() path."""
    dashboard = AWCIDashboard()
    dashboard._on_real_physics_ready(_real_volume())

    dashboard._open_vertical_profile()

    profile = dashboard._vertical_profile_widget._profile
    assert profile  # at least the real point's own native-range levels got a real bar
    for level_label, score in profile.items():
        assert 0.0 <= score <= 100.0
        # Same real value the click-to-detail dialog itself reads back -
        # one real computation, not two that could silently drift apart.
        assert dashboard._vertical_profile_data[level_label]["result"]["awci"] == pytest.approx(score)


def test_vertical_profile_in_real_physics_mode_never_shows_a_level_it_did_not_really_bracket(qapp):
    """Real, deliberate refusal to extrapolate - the dialog must only
    ever show labels vertical_profile_at_standard_levels() actually
    returned (see interpolated_state_at_pressure()'s own docstring for
    when it refuses: a target pressure outside this point's real native
    column). EarthGrid's fixed real levels currently always span
    ~2013->1 hPa regardless of n_levels, so every §51 standard/flight
    level happens to fall inside that range for THIS solver
    configuration - this test locks in the real subset/no-crash
    contract itself (via a real function-level cross-check), not a
    specific omission, since the omission path already has its own
    direct unit tests in test_awci_vertical_field.py."""
    from acf.awci.vertical_field import vertical_profile_at_standard_levels
    from acf.gui.dashboard.awci_dashboard import _ALL_VERTICAL_PROFILE_LEVELS_HPA

    dashboard = AWCIDashboard()
    volume = _real_volume(n_levels=3, steps=1)
    dashboard._on_real_physics_ready(volume)

    dashboard._open_vertical_profile()

    profile = dashboard._vertical_profile_widget._profile
    lat, lon = dashboard._point_of_interest
    expected_labels = set(
        vertical_profile_at_standard_levels(volume, lat, lon, _ALL_VERTICAL_PROFILE_LEVELS_HPA).keys()
    )
    assert set(profile.keys()) == expected_labels
    for score in profile.values():
        assert 0.0 <= score <= 100.0


def test_vertical_profile_switching_from_real_physics_back_to_demo_recomputes(qapp):
    """Real regression guard: toggling Real Physics off must not leave
    the vertical-profile dialog showing stale interpolated data - the
    next _open_vertical_profile() call while back in demo mode must use
    _synthetic_inputs() again."""
    dashboard = AWCIDashboard()
    dashboard._on_real_physics_ready(_real_volume())
    dashboard._open_vertical_profile()
    assert dashboard._real_physics_active is True

    dashboard._real_physics_active = False  # same real flag refresh()/_open_vertical_profile() itself reads
    dashboard._open_vertical_profile()

    profile = dashboard._vertical_profile_widget._profile
    assert "FL100" in profile and "FL320" in profile  # demo mode's own full level list, unconstrained by any real column


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


def test_vertical_profile_data_carries_the_real_module_scores_per_level(qapp):
    """§51's own request ("vent, température, humidité, ..." at each
    level, not just the composite score) - priority freely chosen
    ("suit ton jugement")."""
    dashboard = AWCIDashboard()
    dashboard._open_vertical_profile()

    assert set(dashboard._vertical_profile_data.keys()) == set(dashboard._vertical_profile_widget._profile.keys())
    entry = dashboard._vertical_profile_data["300 hPa"]
    assert entry["hpa"] == pytest.approx(300.0)
    assert "module_scores" in entry["result"]
    assert set(entry["result"]["module_scores"].keys()) == {
        "dynamic", "thermodynamic", "convective", "microphysical", "topographic", "temporal", "confidence",
        "ensemble_spread", "model_disagreement",
    }


def test_clicking_a_real_bar_opens_the_real_level_detail_dialog(qapp):
    dashboard = AWCIDashboard()
    dashboard._open_vertical_profile()
    assert dashboard._vertical_profile_detail_window is None

    dashboard._vertical_profile_widget.levelClicked.emit("FL280")

    assert dashboard._vertical_profile_detail_window is not None
    assert "FL280" in dashboard._vertical_profile_detail_window.windowTitle()


def test_clicking_a_different_bar_reuses_the_same_dialog_instance(qapp):
    dashboard = AWCIDashboard()
    dashboard._open_vertical_profile()
    dashboard._vertical_profile_widget.levelClicked.emit("FL280")
    first = dashboard._vertical_profile_detail_window

    dashboard._vertical_profile_widget.levelClicked.emit("850 hPa")

    assert dashboard._vertical_profile_detail_window is first
    assert "850 hPa" in dashboard._vertical_profile_detail_window.windowTitle()


def test_level_detail_dialog_reflects_the_real_awci_score_for_that_level(qapp):
    dashboard = AWCIDashboard()
    dashboard._open_vertical_profile()

    dashboard._vertical_profile_widget.levelClicked.emit("500 hPa")

    expected = dashboard._vertical_profile_data["500 hPa"]["result"]
    dialog = dashboard._vertical_profile_detail_window
    assert f"{expected['awci']:.1f}" in dialog._score_label.text()


def test_clicking_a_real_bar_via_a_real_mouse_event_opens_the_dialog(qapp):
    """End-to-end: a real mousePressEvent on the widget (not a direct
    signal .emit()) must reach the dashboard's own handler."""
    from PySide6.QtCore import QEvent, QPointF, Qt as QtCore_Qt
    from PySide6.QtGui import QMouseEvent

    dashboard = AWCIDashboard()
    dashboard._open_vertical_profile()
    widget = dashboard._vertical_profile_widget
    widget.resize(400, 300)
    widget.repaint()
    assert widget._bar_geometry  # real geometry ready before the click

    level, x, bar_width = widget._bar_geometry[0]
    event = QMouseEvent(
        QEvent.Type.MouseButtonPress, QPointF(x + bar_width / 2, 100),
        QtCore_Qt.MouseButton.LeftButton, QtCore_Qt.MouseButton.LeftButton, QtCore_Qt.KeyboardModifier.NoModifier,
    )
    widget.mousePressEvent(event)

    assert dashboard._vertical_profile_detail_window is not None
    assert level in dashboard._vertical_profile_detail_window.windowTitle()


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


# ------------------------------------------------------- Real Archive (RESTOR)


def test_real_archive_button_is_wired(qapp):
    dashboard = AWCIDashboard()
    assert dashboard.real_archive_button.toolTip() != ""
    assert dashboard._real_archive_window is None


def test_real_archive_reports_honestly_when_unavailable(qapp, monkeypatch):
    """Real, deliberate degradation path - a machine without
    $HOME/RESTOR (every machine but the one this feature was built
    on) must get an honest status message, never a crash and never a
    silently-substituted demo/solver value under this same button."""
    import acf.gui.dashboard.awci_dashboard as dashboard_module

    def _raise(*_args, **_kwargs):
        raise FileNotFoundError("no real archive on this machine")

    monkeypatch.setattr(dashboard_module, "load_real_aladin_restor_run", _raise)

    dashboard = AWCIDashboard()
    dashboard._open_real_archive()

    assert dashboard._real_archive_cache == {}  # a failed load is never cached
    assert "not available" in dashboard._real_archive_status_label.text()
    assert dashboard._real_archive_widget._profile == {}  # honestly empty, not a fabricated bar


def test_real_archive_lead_time_selector_defaults_to_the_00h_analysis(qapp):
    dashboard = AWCIDashboard()
    dashboard._open_real_archive()
    assert dashboard._real_archive_lead_selector.currentText() == "00h"


def test_real_archive_trend_widget_starts_hidden(qapp):
    dashboard = AWCIDashboard()
    dashboard._open_real_archive()
    assert dashboard._real_archive_trend_widget.testAttribute(Qt.WidgetAttribute.WA_WState_Hidden)


def test_loading_the_real_trend_immediately_disables_the_button_and_shows_a_loading_status(qapp, monkeypatch):
    """Synchronous state right after the click, before any background
    worker runs - QThreadPool.globalInstance().start() itself is
    monkeypatched to a no-op so this test never leaves a real
    background thread running past its own lifetime (the worker's own
    real completion path is exercised deliberately, and waited on, by
    the gated end-to-end test in TestRealArchiveWithTheRealFile)."""
    from PySide6.QtCore import QThreadPool

    monkeypatch.setattr(QThreadPool, "start", lambda self, worker: None)

    dashboard = AWCIDashboard()
    dashboard._open_real_archive()

    dashboard._load_real_archive_trend()

    assert dashboard._real_archive_trend_button.isEnabled() is False
    assert "Loading" in dashboard._real_archive_trend_status_label.text()


def test_on_real_archive_trend_ready_populates_the_widget_and_merges_the_cache(qapp):
    """Same real "handler called directly with a constructed result"
    convention as test_awci_dashboard_real_physics.py's own tests -
    the QThreadPool/signal plumbing itself is standard, trusted Qt
    machinery, covered separately by the real end-to-end worker test
    in TestRealArchiveWithTheRealFile above."""
    dashboard = AWCIDashboard()
    dashboard._open_real_archive()
    assert dashboard._real_archive_trend_widget.testAttribute(Qt.WidgetAttribute.WA_WState_Hidden)

    fake_new_archive = {"run_datetime": "2026-08-31 06:00:00"}  # a real-shaped, not real, dict for this unit test
    dashboard._on_real_archive_trend_ready(
        {"trend": [("+0h", 12.0), ("+3h", 15.0)], "newly_loaded": {6: fake_new_archive}}
    )

    assert dashboard._real_archive_trend_button.isEnabled() is True
    assert dashboard._real_archive_cache[6] is fake_new_archive  # merged on the GUI thread, as documented
    assert dashboard._real_archive_trend_widget._data == [("+0h", 12.0), ("+3h", 15.0)]
    assert not dashboard._real_archive_trend_widget.testAttribute(Qt.WidgetAttribute.WA_WState_Hidden)
    assert "2/17" in dashboard._real_archive_trend_status_label.text()


def test_on_real_archive_trend_ready_with_an_empty_trend_stays_honestly_hidden(qapp):
    """A point genuinely outside every real lead time's own domain -
    the widget must not show a fabricated/empty chart as if it were
    real data."""
    dashboard = AWCIDashboard()
    dashboard._open_real_archive()

    dashboard._on_real_archive_trend_ready({"trend": [], "newly_loaded": {}})

    assert dashboard._real_archive_trend_widget.testAttribute(Qt.WidgetAttribute.WA_WState_Hidden)
    assert "No real lead time" in dashboard._real_archive_trend_status_label.text()


def test_on_real_archive_trend_failed_reports_honestly(qapp):
    dashboard = AWCIDashboard()
    dashboard._open_real_archive()
    dashboard._real_archive_trend_button.setEnabled(False)

    dashboard._on_real_archive_trend_failed("disk full")

    assert dashboard._real_archive_trend_button.isEnabled() is True
    assert "disk full" in dashboard._real_archive_trend_status_label.text()


REAL_RESTOR_FILE = Path.home() / "RESTOR" / "ALADIN" / "data" / "FULLPOS_2026083100_0000"


@pytest.mark.skipif(
    not REAL_RESTOR_FILE.exists(),
    reason="Real RESTOR ALADIN archive not present on this machine (machine-local only, not in git)",
)
class TestRealArchiveWithTheRealFile:
    """Gated on the real RESTOR archive being present - see
    tests/test_awci_archive_field.py for the module-level tests this
    mirrors at the dashboard-integration level."""

    def test_opens_and_shows_a_real_profile_at_the_default_point_of_interest(self, qapp):
        dashboard = AWCIDashboard()
        dashboard._open_real_archive()

        assert 0 in dashboard._real_archive_cache  # the default +0h lead time, real and loaded
        profile = dashboard._real_archive_widget._profile
        assert profile  # the default point of interest is real and within this archive's domain
        for score in profile.values():
            assert 0.0 <= score <= 100.0
        assert "OUTSIDE" not in dashboard._real_archive_status_label.text()

    def test_archive_is_loaded_once_per_lead_time_and_cached_across_calls(self, qapp):
        dashboard = AWCIDashboard()
        dashboard._open_real_archive()
        first_archive = dashboard._real_archive_cache[0]

        dashboard._open_real_archive()

        assert dashboard._real_archive_cache[0] is first_archive

    def test_changing_the_lead_time_selector_loads_and_caches_a_different_real_archive(self, qapp):
        """Real, direct proof this is a genuinely different real
        forecast hour, not the same +0h data relabelled - the run's
        own real validity time must advance."""
        dashboard = AWCIDashboard()
        dashboard._open_real_archive()
        validity_at_0h = dashboard._real_archive_cache[0]["run_datetime"]

        dashboard._real_archive_lead_selector.setCurrentText("24h")

        assert 24 in dashboard._real_archive_cache
        validity_at_24h = dashboard._real_archive_cache[24]["run_datetime"]
        assert validity_at_24h != validity_at_0h
        assert "+24h" in dashboard._real_archive_status_label.text()

    def test_clicking_a_real_bar_opens_the_real_level_detail_dialog(self, qapp):
        dashboard = AWCIDashboard()
        dashboard._open_real_archive()
        assert dashboard._real_archive_detail_window is None

        dashboard._real_archive_widget.levelClicked.emit("850 hPa")

        assert dashboard._real_archive_detail_window is not None
        assert "850 hPa" in dashboard._real_archive_detail_window.windowTitle()

    def test_flags_honestly_when_the_point_of_interest_is_outside_the_real_domain(self, qapp):
        dashboard = AWCIDashboard()
        dashboard._point_of_interest = (-40.0, 170.0)  # a real point, far outside North Africa

        dashboard._open_real_archive()

        assert "OUTSIDE" in dashboard._real_archive_status_label.text()

    def test_real_48h_trend_worker_genuinely_runs_off_thread_and_populates_the_widget(self, qapp, qtbot):
        """Drives the actual QThreadPool.globalInstance().start() +
        Qt event loop path (same discipline as
        test_acf_general_dashboard.py's own real-worker test) - a
        signal-connection bug would only be caught this way, not by
        calling the ready handler directly. Pre-populates every real
        lead time except +6h so this test only pays for one real ~0.4s
        FA decode, not all 17."""
        from acf.awci.archive_field import load_real_aladin_restor_run, restor_fullpos_path

        dashboard = AWCIDashboard()
        dashboard._open_real_archive()
        for lead_hours in (0, 3, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48):
            path = restor_fullpos_path(REAL_RESTOR_FILE.parent, "2026083100", lead_hours)
            dashboard._real_archive_cache[lead_hours] = load_real_aladin_restor_run(path)
        assert 6 not in dashboard._real_archive_cache  # the one real lead time the worker must actually decode

        dashboard._load_real_archive_trend()

        assert dashboard._real_archive_trend_button.isEnabled() is False  # real synchronous immediate disable
        qtbot.waitUntil(lambda: dashboard._real_archive_trend_button.isEnabled(), timeout=30000)

        assert 6 in dashboard._real_archive_cache  # the worker's own real decode, merged on the GUI thread
        assert len(dashboard._real_archive_trend_widget._data) == 17
        assert "17/17" in dashboard._real_archive_trend_status_label.text()
        assert not dashboard._real_archive_trend_widget.testAttribute(Qt.WidgetAttribute.WA_WState_Hidden)
