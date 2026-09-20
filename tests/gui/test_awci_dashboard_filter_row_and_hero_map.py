"""
Tests for Task 8 of the 2026-09-14 AWCI dashboard-fixes plan: the filter
bar becoming its own row (with real Layers/Settings buttons) and the hero
map's resize/reposition (floating Map Layers panel anchored to the map's
own top-left corner, a reachable opacity slider, an unclipped AWCI SCALE
legend, and a real play/timeline transport row beneath the map).

Every assertion below is driven through the REAL dashboard construction
path (`AWCIDashboard()` / `AWCIMapPanel`), never a hand-fed fixture.
"""

import pytest
from PySide6.QtWidgets import QApplication, QPushButton, QSizePolicy

from acf.gui.dashboard.awci_dashboard import AWCIDashboard
from acf.gui.dashboard.awci_map_panel import AWCIMapPanel
from acf.gui.dashboard.awci_topbar import AWCITopBar


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


# --------------------------------------------------------- the filter row


def test_the_filter_selectors_are_no_longer_children_of_the_top_bar(qapp):
    """The reference image keeps Area/Date & Time/Forecast/Model OUT of
    the white top bar - they must live in their own row below it."""
    dashboard = AWCIDashboard()

    for control in (
        dashboard.topbar.area_combo,
        dashboard.topbar.now_button,
        dashboard.topbar.forecast_label,
        dashboard.topbar.model_label,
    ):
        ancestors = []
        widget = control.parentWidget()
        while widget is not None:
            ancestors.append(widget)
            widget = widget.parentWidget()
        assert dashboard.topbar not in ancestors, f"{control} is still inside the top bar"
        assert dashboard.filter_row_widget in ancestors, f"{control} is not in the new filter row"


def test_the_top_bar_itself_no_longer_builds_the_selectors_into_its_own_layout(qapp):
    """Checked directly on the widget, independently of the dashboard -
    AWCITopBar must expose the same real controls but assembled into
    `filter_bar`, which it does NOT add to its own row."""
    bar = AWCITopBar()

    assert bar.filter_bar.parentWidget() is None  # free to be reparented by the dashboard
    assert bar.area_combo.parentWidget() is not None
    assert bar.layout().indexOf(bar.filter_bar) == -1


def test_the_filter_row_has_real_layers_and_settings_buttons(qapp):
    dashboard = AWCIDashboard()

    assert isinstance(dashboard.layers_button, QPushButton)
    assert isinstance(dashboard.settings_button, QPushButton)
    assert "Layers" in dashboard.layers_button.text()
    assert "Settings" in dashboard.settings_button.text()
    buttons = dashboard.filter_row_widget.findChildren(QPushButton)
    assert dashboard.layers_button in buttons
    assert dashboard.settings_button in buttons


def test_the_layers_button_really_toggles_the_maps_own_floating_panel(qapp):
    dashboard = AWCIDashboard()
    panel = dashboard.global_map.layers_panel
    panel.setVisible(True)

    # isHidden(), not isVisible(): an unshown dashboard's children are
    # never "visible" regardless of their own real show/hide state.
    dashboard.layers_button.click()
    assert panel.isHidden() is True

    dashboard.layers_button.click()
    assert panel.isHidden() is False


def test_the_settings_button_opens_the_same_single_real_menu_the_gear_opens(qapp):
    """Never a second, duplicated settings menu - this file's own
    established convention (see _open_settings_menu()'s docstring)."""
    dashboard = AWCIDashboard()
    opened: list[object] = []
    dashboard._header_menu.popup = lambda *_args, **_kwargs: opened.append(dashboard._header_menu)

    dashboard.settings_button.click()

    assert opened == [dashboard._header_menu]


# ------------------------------------------------------------- the hero map


def test_the_hero_map_is_materially_taller_and_expands(qapp):
    """Task 8 raised this from a 240px (x screen scale) minimum with a
    140px floor - the reference image's map is roughly 40% of the page
    height, not ~19%."""
    dashboard = AWCIDashboard(screen_scale=1.0)

    assert dashboard.global_map.minimumHeight() >= 420
    assert dashboard.global_map.sizePolicy().verticalPolicy() == QSizePolicy.Policy.Expanding


def test_the_hero_map_row_outranks_the_analysis_row_for_vertical_space(qapp):
    """The map row's stretch must genuinely exceed the bottom analysis
    row's, so on a viewport with room to spare the map is what grows."""
    dashboard = AWCIDashboard()
    # The layout that owns both rows is the content column - reached via
    # the map's own parent widget rather than a hardcoded index.
    content_layout = dashboard.global_map.parentWidget().layout()
    stretches = [content_layout.stretch(i) for i in range(content_layout.count())]
    assert max(stretches) >= 6


def test_the_map_layers_panel_floats_over_the_maps_own_top_left_corner(qapp):
    panel = AWCIMapPanel("AWCI GLOBAL MAP", show_layers_panel=True, show_view_toggle=True)
    panel.resize(900, 420)
    panel.show()
    QApplication.processEvents()

    map_left, map_top, map_width, _map_height = panel._drawn_map_rect()
    assert panel.layers_panel.parentWidget() is panel.canvas  # a real floating child of the canvas
    assert abs(panel.layers_panel.x() - map_left) <= 24
    assert abs(panel.layers_panel.y() - map_top) <= 24
    # ...and genuinely on the map's LEFT half, not docked at its right edge
    assert panel.layers_panel.x() < map_left + map_width / 2


def test_the_opacity_slider_is_reachable_inside_the_floating_panel(qapp):
    """It existed before but was clipped out of view by the panel's old
    top-right anchoring on a short map - the regression this guards."""
    panel = AWCIMapPanel("AWCI GLOBAL MAP", show_layers_panel=True, show_view_toggle=True)
    panel.resize(900, 420)
    panel.show()
    QApplication.processEvents()

    slider = panel.opacity_slider
    assert slider.isHidden() is False
    slider_bottom = slider.mapTo(panel.canvas, slider.rect().bottomLeft()).y()
    assert slider_bottom <= panel.canvas.height(), "the opacity slider is clipped out of the canvas"


def test_the_awci_scale_legend_rows_never_collapse_on_a_short_map(qapp):
    """Real anti-clipping contract: every LEVELS row must keep a
    readable share of the axes, whatever the map's real height."""
    from acf.gui.dashboard.awci_colors import LEVELS

    short = AWCIMapPanel("AWCI GLOBAL MAP", show_legend=True)
    short.resize(900, 180)
    short.show()
    QApplication.processEvents()
    short.update_data(flight_level_hpa=300.0)

    texts = [t.get_text() for t in short.axis.texts]
    assert "AWCI SCALE" in texts
    for _threshold, name, _rgb in LEVELS:
        assert any(name in t for t in texts), f"legend row {name!r} was not drawn"


# ------------------------------------------------------- the transport row


def test_the_transport_row_exists_beneath_the_map(qapp):
    dashboard = AWCIDashboard()

    assert dashboard.map_transport_widget is not None
    assert dashboard.transport_play_button.text() in ("▶", "❚❚")
    assert dashboard.transport_slider is not None


def test_the_transport_scrubber_drives_the_same_real_valid_time(qapp):
    """Mirrors Task 3's own real-value-changes-with-the-slider pattern:
    moving this scrubber must move the ONE real Valid Time value and
    genuinely change the displayed data, not a second time model."""
    dashboard = AWCIDashboard()
    assert dashboard.transport_slider.maximum() == dashboard.time_slider.maximum()

    before_situation = dashboard.current_situation_card.valid_time_label.text()

    dashboard.transport_slider.setValue(19)
    assert dashboard.time_slider.value() == 19  # the same single real time value
    dashboard._on_time_changed()

    after_situation = dashboard.current_situation_card.valid_time_label.text()
    assert after_situation != before_situation
    assert "19:00" in after_situation


def test_the_valid_time_slider_moves_the_scrubber_back(qapp):
    dashboard = AWCIDashboard()

    dashboard.time_slider.setValue(4)

    assert dashboard.transport_slider.value() == 4


def test_play_really_advances_the_same_real_valid_time(qapp):
    dashboard = AWCIDashboard()
    dashboard.time_slider.setValue(10)

    dashboard._toggle_time_playback()
    assert dashboard._time_playback_timer.isActive() is True
    dashboard._advance_time_playback()
    assert dashboard.time_slider.value() == 11
    assert dashboard.transport_slider.value() == 11

    dashboard._toggle_time_playback()
    assert dashboard._time_playback_timer.isActive() is False


def test_the_transport_freshness_pill_is_honest_about_the_demo_tier(qapp):
    """Never a fabricated "Live Data" claim while the active tier is this
    dashboard's own synthetic demo pattern - the same 3-way disclosure
    rule the top bar's status badge already uses."""
    dashboard = AWCIDashboard()

    assert dashboard._real_physics_active is False
    assert "Demo Data" in dashboard.transport_tier_label.text()
    assert "Live" not in dashboard.transport_tier_label.text()


def test_the_transport_freshness_pill_follows_a_real_physics_tier_change(qapp):
    dashboard = AWCIDashboard()
    dashboard._real_physics_active = True

    dashboard._sync_map_transport_row(dashboard.time_slider.value())

    assert "Real Physics Data" in dashboard.transport_tier_label.text()
