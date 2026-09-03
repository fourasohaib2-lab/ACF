"""
Tests for AWCIMapPanel's reference-mockup-fidelity features (explicit
user request "je veux garder le meme theme pour les deux en suivant
cette photo", the photo being this dashboard's own original reference
mockup): the AWCI SCALE legend, RENDERED/FLIGHT LEVEL info boxes, the
floating Point Information card, the vertical zoom/download icon
stack, and the Layers panel.
"""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt

from acf.gui.dashboard.awci_colors import LEVELS
from acf.gui.dashboard.awci_map_panel import AWCIMapPanel, pressure_to_flight_level_ft


def test_pressure_to_flight_level_is_a_real_standard_conversion():
    # FL300 (~9000m) is a real, well-known ISA pressure-altitude pair:
    # ~300 hPa. FL100 (~3000m) is ~700 hPa. Both real, standard values.
    assert 29000 < pressure_to_flight_level_ft(300.0) < 31000
    assert 9500 < pressure_to_flight_level_ft(700.0) < 10500


def test_pressure_to_flight_level_is_monotonic_with_altitude():
    """Lower pressure = higher altitude - a real physical property, not
    an arbitrary lookup."""
    assert pressure_to_flight_level_ft(200.0) > pressure_to_flight_level_ft(500.0) > pressure_to_flight_level_ft(900.0)


def test_legend_and_info_boxes_off_by_default(qtbot):
    """No visual clutter unless explicitly requested - matches the
    reference, which only shows these on its global map."""
    panel = AWCIMapPanel("AWCI GLOBAL MAP")
    qtbot.addWidget(panel)
    assert panel._show_legend is False
    assert panel._show_info_boxes is False
    assert panel._show_layers_panel is False
    assert not hasattr(panel, "layers_panel")


def test_legend_and_info_boxes_render_without_exception_when_enabled(qtbot):
    panel = AWCIMapPanel("AWCI GLOBAL MAP", show_legend=True, show_info_boxes=True)
    qtbot.addWidget(panel)
    # update_data() already ran once in __init__ - re-run explicitly to
    # be sure no exception is raised with both real overlays enabled.
    panel.update_data(flight_level_hpa=300.0)
    assert panel.status()["has_contour"] is True


def test_legend_uses_the_real_shared_awci_levels_not_a_separate_scale(qtbot):
    """Real proof the legend draws from acf.gui.dashboard.awci_colors.LEVELS
    - the same real thresholds every other AWCI widget uses - not a
    separately hand-typed scale that could silently drift out of sync."""
    panel = AWCIMapPanel("AWCI GLOBAL MAP", show_legend=True)
    qtbot.addWidget(panel)
    panel.update_data()
    texts = [t.get_text() for t in panel.axis.texts]
    for threshold, name, _rgb in LEVELS:
        assert any(f"{threshold:g}" in txt and name in txt for txt in texts)


def test_point_marker_with_a_real_score_draws_a_point_information_card(qtbot):
    panel = AWCIMapPanel("AWCI REGIONAL MAP")
    qtbot.addWidget(panel)

    panel.set_point_marker(34.5, 12.3, awci_score=67.0)

    annotation_texts = [a.get_text() for a in panel.axis.texts]
    assert any("POINT INFORMATION" in txt and "67" in txt for txt in annotation_texts)


def test_point_marker_without_a_score_draws_no_card(qtbot):
    """Backward compatible - a bare marker (no real score available)
    must not draw a fabricated info card."""
    panel = AWCIMapPanel("AWCI REGIONAL MAP")
    qtbot.addWidget(panel)

    panel.set_point_marker(34.5, 12.3)

    annotation_texts = [a.get_text() for a in panel.axis.texts]
    assert not any("POINT INFORMATION" in txt for txt in annotation_texts)


def test_vertical_zoom_and_download_buttons_are_real_and_wired(qtbot):
    panel = AWCIMapPanel("AWCI GLOBAL MAP")
    qtbot.addWidget(panel)
    before = panel.camera.current_extent()

    qtbot.mouseClick(panel.zoom_in_button, Qt.MouseButton.LeftButton)

    after = panel.camera.current_extent()
    assert (after[1] - after[0]) < (before[1] - before[0])
    assert panel.download_button is not None  # real button exists (file-save path exercised separately)


def test_layers_panel_awci_checkbox_genuinely_toggles_contour_visibility(qtbot):
    panel = AWCIMapPanel("AWCI GLOBAL MAP", show_layers_panel=True)
    qtbot.addWidget(panel)
    assert panel._contour.get_visible() is True

    panel.awci_layer_checkbox.setChecked(False)

    assert panel._contour.get_visible() is False


def test_layers_panel_other_layers_are_honestly_disabled_not_fake_toggles():
    """No fabricated interactivity - every layer this panel has no real
    data source for is shown genuinely non-interactive."""
    panel = AWCIMapPanel("AWCI GLOBAL MAP", show_layers_panel=True)
    for name, checkbox in panel.disabled_layer_checkboxes.items():
        assert checkbox.isEnabled() is False, f"{name} checkbox should be disabled (no real data source)"
        assert checkbox.isChecked() is False


def test_layers_panel_state_survives_a_real_data_refresh(qtbot):
    """update_data() (e.g. from the time_slider) must not silently
    re-enable a layer the user turned off."""
    panel = AWCIMapPanel("AWCI GLOBAL MAP", show_layers_panel=True)
    qtbot.addWidget(panel)
    panel.awci_layer_checkbox.setChecked(False)

    panel.update_data(flight_level_hpa=500.0, time_offset_hours=3.0)

    assert panel._contour.get_visible() is False


@pytest.mark.parametrize("show_legend,show_info_boxes,show_layers_panel", [(True, True, True)])
def test_full_reference_fidelity_panel_constructs_without_exception(qtbot, show_legend, show_info_boxes, show_layers_panel):
    panel = AWCIMapPanel(
        "AWCI GLOBAL MAP", show_legend=show_legend, show_info_boxes=show_info_boxes, show_layers_panel=show_layers_panel
    )
    qtbot.addWidget(panel)
    panel.set_point_marker(10.0, 20.0, awci_score=42.0)
    panel.resize(900, 600)
    qtbot.wait(10)
    assert panel.status()["has_contour"] is True
