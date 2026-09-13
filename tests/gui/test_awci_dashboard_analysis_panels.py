"""
Tests for AWCIDashboard's real "5 analysis panels" bottom row - Vertical
Cross Section / Atmospheric Profile / Flight Route Analysis / Time
Evolution (AWCI) / AWCI Vertical Profile (added 2026-09-13, docs/
reference/awci_dashboard_reference.png, Phase 5/6 of the AWCI redesign,
explicit user request "tu peux enlever toutes l'ancienne paramètres...
je veux que tout le dashboard soit exactement comme la photo à 100%").
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.awci.calculator import AWCICalculator
from acf.gui.dashboard.acf_workstation_sounding_panel import ACFVerticalSoundingWidget
from acf.gui.dashboard.awci_cross_section import AWCICrossSection
from acf.gui.dashboard.awci_dashboard import _ALL_VERTICAL_PROFILE_LEVELS_HPA, AWCIDashboard
from acf.gui.dashboard.awci_evolution_chart import AWCIEvolutionChart
from acf.gui.dashboard.awci_route_chart import AWCIRouteChart
from acf.gui.dashboard.awci_synthetic_field import _synthetic_inputs
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
                time_offset_hours=float(offset),
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
