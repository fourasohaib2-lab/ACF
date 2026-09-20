"""
Tests for AWCIDashboard's real "5 analysis panels" bottom row - Vertical
Cross Section / Atmospheric Profile / Flight Route Analysis / Time
Evolution (AWCI) / AWCI Vertical Profile (added 2026-09-13, docs/
reference/awci_dashboard_reference.png, Phase 5/6 of the AWCI redesign,
explicit user request "tu peux enlever toutes l'ancienne paramètres...
je veux que tout le dashboard soit exactement comme la photo à 100%").
"""

from __future__ import annotations

import numpy as np
import pytest
from PySide6.QtWidgets import QApplication

from acf.awci.calculator import AWCICalculator
from acf.gui.dashboard.acf_workstation_sounding_panel import ACFVerticalSoundingWidget
from acf.gui.dashboard.awci_cross_section import AWCICrossSection
from acf.gui.dashboard.awci_dashboard import _ALL_VERTICAL_PROFILE_LEVELS_HPA, _AIRPORTS, AWCIDashboard
from acf.gui.dashboard.awci_evolution_chart import AWCIEvolutionChart
from acf.gui.dashboard.awci_route_chart import AWCIRouteChart
from acf.gui.dashboard.awci_synthetic_field import _synthetic_inputs, route_profile
from acf.gui.dashboard.awci_vertical_profile import AWCIVerticalProfile


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


# ------------------------------------------------------- panel presence


def test_all_five_real_analysis_widgets_exist_and_are_the_expected_real_types(qapp):
    dashboard = AWCIDashboard()
    assert isinstance(dashboard.cross_section, AWCICrossSection)
    assert isinstance(dashboard.atmospheric_profile, ACFVerticalSoundingWidget)
    assert isinstance(dashboard.route_chart, AWCIRouteChart)
    assert isinstance(dashboard.evolution_chart, AWCIEvolutionChart)
    assert isinstance(dashboard.vertical_profile_panel, AWCIVerticalProfile)


def test_relocated_widgets_are_not_hidden_in_their_new_analysis_panel(qapp):
    """Real proof these are genuinely relocated (still in a real, shown
    layout) - not left hidden like the old row1/row2 widgets they
    replaced (self.radar, self.regional_map, ...)."""
    dashboard = AWCIDashboard()
    for widget in (
        dashboard.cross_section,
        dashboard.atmospheric_profile,
        dashboard.route_chart,
        dashboard.route_selector_widget,
        dashboard.evolution_chart,
        dashboard.time_control_widget,
        dashboard.vertical_profile_panel,
    ):
        # explicit .hide() was never called on these (unlike self.radar/
        # self.regional_map/...) - Qt's own "not explicitly hidden" flag,
        # not isVisible() (which is always False before .show()).
        assert not widget.isHidden(), widget


# --------------------------------------------- _compute_vertical_profile


def test_compute_vertical_profile_matches_a_direct_recomputation_in_demo_mode(qapp):
    """Real proof: the embedded live panel's own numbers are not a
    fabricated/guessed profile - each real level matches an independent
    direct call to the SAME real AWCICalculator/_synthetic_inputs
    pipeline at that level's real pressure, at the dashboard's current
    real point of interest."""
    dashboard = AWCIDashboard()
    profile, data, _suggestion = dashboard._compute_vertical_profile()

    assert set(profile) == set(_ALL_VERTICAL_PROFILE_LEVELS_HPA)
    for level_label, hpa in _ALL_VERTICAL_PROFILE_LEVELS_HPA.items():
        raw = _synthetic_inputs(*dashboard._point_of_interest, flight_level_hpa=hpa)
        expected = AWCICalculator().calculate(raw)["awci"]
        assert profile[level_label] == pytest.approx(expected)
        assert data[level_label]["hpa"] == pytest.approx(hpa)


def test_sync_vertical_profile_panel_matches_vertical_profile_data(qapp):
    """_sync_vertical_profile_panel() stores both the plotted profile
    (self.vertical_profile_panel._profile) and the real per-level detail
    data (self._vertical_profile_data, read by _on_vertical_profile_
    level_clicked()) from the SAME _compute_vertical_profile() call -
    never two independent computations of the same real point."""
    dashboard = AWCIDashboard()
    dashboard._sync_vertical_profile_panel()

    assert set(dashboard.vertical_profile_panel._profile.keys()) == set(dashboard._vertical_profile_data.keys())
    for level_label, score in dashboard.vertical_profile_panel._profile.items():
        assert dashboard._vertical_profile_data[level_label]["result"]["awci"] == pytest.approx(score)


def test_sync_vertical_profile_panel_is_called_on_every_real_per_point_refresh(qapp):
    dashboard = AWCIDashboard()
    dashboard.vertical_profile_panel._profile = {}  # clear whatever __init__'s own refresh() set

    dashboard.refresh()

    assert dashboard.vertical_profile_panel._profile  # real, non-empty after a real refresh


# --------------------------------------------------------- evolution chart


def test_evolution_chart_matches_a_direct_recomputation_of_the_real_pm6h_series(qapp):
    """Real proof: the embedded "Time Evolution (AWCI)" panel's demo-
    mode series is not fabricated - it matches an independent direct
    recomputation of the same real +/-6h AWCICalculator/_synthetic_
    inputs sampling refresh() itself performs at the point of interest."""
    dashboard = AWCIDashboard()
    dashboard.refresh()

    current_hour = dashboard.time_slider.value()
    expected_values = [
        AWCICalculator().calculate(
            _synthetic_inputs(
                *dashboard._point_of_interest,
                flight_level_hpa=dashboard._current_flight_level_hpa,
                time_offset_hours=float(current_hour + offset),
            )
        )["awci"]
        for offset in range(-6, 7, 2)
    ]
    plotted_mean = list(dashboard.evolution_chart.axis.lines[0].get_ydata())
    assert plotted_mean == pytest.approx(expected_values)


def test_atmospheric_profile_stays_on_its_own_honest_placeholder_in_demo_mode(qapp):
    """No real 3D volume exists in demo mode - ACFVerticalSoundingWidget
    must show its own honest "click a map" placeholder, never a
    fabricated sounding (see that widget's own module docstring)."""
    dashboard = AWCIDashboard()
    dashboard.refresh()
    assert dashboard.atmospheric_profile._point is None


# ------------------------ evolution chart: Global/Route/Airport toggle (§22)


def test_evolution_toggle_defaults_to_global_with_global_button_checked(qapp):
    dashboard = AWCIDashboard()
    assert dashboard._evolution_view_mode == "global"
    assert dashboard.evolution_view_buttons["global"].isChecked()
    assert not dashboard.evolution_view_buttons["route"].isChecked()
    assert not dashboard.evolution_view_buttons["airport"].isChecked()


def test_clicking_route_button_checks_it_exclusively_and_updates_mode(qapp):
    dashboard = AWCIDashboard()
    dashboard.evolution_view_buttons["route"].click()

    assert dashboard._evolution_view_mode == "route"
    assert dashboard.evolution_view_buttons["route"].isChecked()
    assert not dashboard.evolution_view_buttons["global"].isChecked()
    assert not dashboard.evolution_view_buttons["airport"].isChecked()


def test_clicking_airport_button_checks_it_exclusively_and_updates_mode(qapp):
    dashboard = AWCIDashboard()
    dashboard.evolution_view_buttons["airport"].click()

    assert dashboard._evolution_view_mode == "airport"
    assert dashboard.evolution_view_buttons["airport"].isChecked()
    assert not dashboard.evolution_view_buttons["global"].isChecked()
    assert not dashboard.evolution_view_buttons["route"].isChecked()


def test_route_mode_series_matches_a_direct_recomputation_of_route_profile(qapp):
    """Real proof the "Route" mode is not fabricated - its plotted
    mean/max match an independent direct recomputation via the same
    real route_profile() sampled at the same real active route/offsets
    _compute_demo_evolution_series() itself uses."""
    dashboard = AWCIDashboard()
    dashboard.refresh()
    dashboard.evolution_view_buttons["route"].click()

    current_hour = dashboard.time_slider.value()
    expected_hours = [float((current_hour + offset) % 24) for offset in range(-6, 7, 2)]
    expected_means = []
    expected_maxes = []
    for offset in range(-6, 7, 2):
        _distances, scores = route_profile(
            dashboard._regional_route[0][:2], dashboard._regional_route[1][:2],
            n_points=40, flight_level_hpa=850.0, time_offset_hours=float(current_hour + offset),
        )
        expected_means.append(float(np.mean(scores)))
        expected_maxes.append(float(np.max(scores)))

    plotted_hours = list(dashboard.evolution_chart.axis.lines[0].get_xdata())
    plotted_mean = list(dashboard.evolution_chart.axis.lines[0].get_ydata())
    plotted_max = list(dashboard.evolution_chart.axis.lines[1].get_ydata())
    assert plotted_hours == pytest.approx(expected_hours)
    assert plotted_mean == pytest.approx(expected_means)
    assert plotted_max == pytest.approx(expected_maxes)


def test_route_mode_mean_and_max_genuinely_differ_a_route_is_not_one_point():
    """Unlike "global"/"airport" (a single point - mean == max by
    construction), a route spans real distinct points, so its real
    mean and max must genuinely differ at at least one real offset -
    proof this mode is actually richer, not a relabeled duplicate."""
    dashboard = AWCIDashboard()
    dashboard.refresh()

    _hours, means, maxes = dashboard._compute_demo_evolution_series("route")

    assert means != maxes


def test_global_and_airport_modes_have_identical_mean_and_max_a_single_point_has_no_spread(qapp):
    dashboard = AWCIDashboard()
    dashboard.refresh()

    _hours_g, means_g, maxes_g = dashboard._compute_demo_evolution_series("global")
    _hours_a, means_a, maxes_a = dashboard._compute_demo_evolution_series("airport")

    assert means_g == maxes_g
    assert means_a == maxes_a


def test_airport_mode_series_matches_a_direct_recomputation_at_the_selected_departure_airport(qapp):
    dashboard = AWCIDashboard()
    dashboard.refresh()
    dashboard.evolution_view_buttons["airport"].click()

    icao = dashboard.route_from_selector.currentData()
    lat, lon, _name = _AIRPORTS[icao]
    current_hour = dashboard.time_slider.value()
    expected_values = [
        AWCICalculator().calculate(
            _synthetic_inputs(lat, lon, flight_level_hpa=dashboard._current_flight_level_hpa, time_offset_hours=float(current_hour + offset))
        )["awci"]
        for offset in range(-6, 7, 2)
    ]

    plotted_mean = list(dashboard.evolution_chart.axis.lines[0].get_ydata())
    assert plotted_mean == pytest.approx(expected_values)


def test_refresh_redraws_the_currently_selected_mode_not_always_global(qapp):
    """A real refresh() (e.g. moving the Valid Time slider) must
    respect whichever mode the user last picked, not silently reset to
    "global" - see _refresh_evolution_chart()'s own docstring."""
    dashboard = AWCIDashboard()
    dashboard.evolution_view_buttons["route"].click()

    dashboard.refresh()

    assert dashboard._evolution_view_mode == "route"
    _hours, means, maxes = dashboard._compute_demo_evolution_series("route")
    plotted_mean = list(dashboard.evolution_chart.axis.lines[0].get_ydata())
    assert plotted_mean == pytest.approx(means)


# ------------------------------------------- real analysis-row height
#
# Regression tests for 2026-09-20, Task 2 of the AWCI final-polish plan.
# The 5 analysis cards used to render 572px tall (measured) against the
# reference image's own ~250px card - docs/reference/awci_dashboard_
# reference.png is 1536x1024 and its analysis cards span y~650..900, i.e.
# ~24% of the image height. The real cause was NOT the wrapper's
# setMinimumHeight() floor but the matplotlib Figures' own preferred
# sizes: FigureCanvasQTAgg reports a Figure's inch size x dpi verbatim as
# its Qt sizeHint, and two of these panels were left at matplotlib's
# 6.4x4.8in default, i.e. a 480px vertical ask each, while
# AWCIVerticalProfile hard-coded a 300px sizeHint.


def _analysis_card_height(dashboard: AWCIDashboard) -> int:
    """The real rendered height of the analysis row's first card (all
    five share one QHBoxLayout row, so they share a height)."""
    return dashboard.cross_section.parentWidget().height()


def test_every_analysis_canvas_asks_for_a_height_near_the_reference_card_not_matplotlibs_default(qapp):
    dashboard = AWCIDashboard(screen_scale=1.0)

    for chart in (
        dashboard.cross_section,
        dashboard.atmospheric_profile,
        dashboard.route_chart,
        dashboard.evolution_chart,
    ):
        hint = chart.sizeHint().height()
        assert hint < 250, f"{type(chart).__name__} still asks for {hint}px of preferred height"
        # ...but not so small that its axis labels/title lose their room.
        assert hint >= 60

    assert dashboard.vertical_profile_panel.sizeHint().height() < 250


def test_the_real_analysis_row_renders_near_the_reference_images_own_card_proportion(qapp):
    from PySide6.QtWidgets import QMainWindow, QScrollArea

    dashboard = AWCIDashboard(screen_scale=1.0)
    window = QMainWindow()
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(dashboard)
    window.setCentralWidget(scroll)
    window.resize(1920, 1080)
    window.show()
    for _ in range(6):
        qapp.processEvents()

    height = _analysis_card_height(dashboard)
    # Reference proportion is ~24% of the viewport; 33% is a real
    # regression guard (the old row was 53% of a 1080p viewport), not a
    # claim of pixel-exact parity.
    assert height < 0.33 * scroll.viewport().height(), f"analysis row is {height}px tall"
    assert height > 150, "the row must not collapse to an illegible sliver"


def test_the_analysis_row_height_still_scales_with_the_real_screen_scale(qapp):
    """The shrink must not have replaced the real per-screen adaptability
    with a fixed pixel value (compute_screen_scale's own contract)."""
    large = AWCIDashboard(screen_scale=1.0)
    small = AWCIDashboard(screen_scale=0.6)

    assert small.cross_section.sizeHint().height() < large.cross_section.sizeHint().height()
    assert small.vertical_profile_panel.sizeHint().height() < large.vertical_profile_panel.sizeHint().height()


def test_other_callers_of_these_shared_widgets_keep_their_own_original_sizes(qapp):
    """ACFVerticalSoundingWidget (ACF Scientific Workstation) and
    AWCIVerticalProfile (the vertical-profile dialog / real-archive
    view) are shared widgets - only the AWCI dashboard's own instances
    are shrunk, via explicit calls, never by changing their defaults."""
    assert ACFVerticalSoundingWidget().sizeHint().height() > 400
    assert AWCIVerticalProfile().sizeHint().height() == 300
    assert AWCIEvolutionChart().sizeHint().height() > 400
