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
from acf.gui.dashboard.awci_map_panel import (
    AWCIMapPanel,
    flight_level_ft_to_pressure_hpa,
    pressure_to_flight_level_ft,
)


def test_pressure_to_flight_level_is_a_real_standard_conversion():
    # FL300 (~9000m) is a real, well-known ISA pressure-altitude pair:
    # ~300 hPa. FL100 (~3000m) is ~700 hPa. Both real, standard values.
    assert 29000 < pressure_to_flight_level_ft(300.0) < 31000
    assert 9500 < pressure_to_flight_level_ft(700.0) < 10500


def test_pressure_to_flight_level_is_monotonic_with_altitude():
    """Lower pressure = higher altitude - a real physical property, not
    an arbitrary lookup."""
    assert pressure_to_flight_level_ft(200.0) > pressure_to_flight_level_ft(500.0) > pressure_to_flight_level_ft(900.0)


def test_flight_level_ft_to_pressure_hpa_is_the_real_algebraic_inverse():
    for hpa in (1013.25, 850.0, 700.0, 500.0, 300.0, 250.0, 200.0):
        ft = pressure_to_flight_level_ft(hpa)
        back = flight_level_ft_to_pressure_hpa(ft)
        assert back == pytest.approx(hpa, abs=0.05)


def test_flight_level_ft_to_pressure_hpa_known_values():
    """FL280/FL320 (28000/32000 ft) - real, independently verifiable
    ISA pressure-altitude values."""
    assert flight_level_ft_to_pressure_hpa(28000.0) == pytest.approx(329.15, abs=0.5)
    assert flight_level_ft_to_pressure_hpa(32000.0) == pytest.approx(274.32, abs=0.5)


def test_flight_level_ft_to_pressure_hpa_is_monotonic():
    """Higher altitude = lower pressure - a real physical property."""
    assert flight_level_ft_to_pressure_hpa(32000.0) < flight_level_ft_to_pressure_hpa(28000.0) < flight_level_ft_to_pressure_hpa(0.0)


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


def test_layers_panel_extra_layers_are_real_working_toggles(qtbot):
    """Real regression guard (added 2026-09-03, explicit user request
    "je veux rendre tout les boutons de awci en marche"): every extra
    layer checkbox is a real, enabled toggle that shows/hides a real
    matplotlib contour built from awci_layer_grids() - not a fabricated
    interactivity, and not honestly-disabled decoration either."""
    panel = AWCIMapPanel("AWCI GLOBAL MAP", show_layers_panel=True)
    qtbot.addWidget(panel)
    for name, checkbox in panel.extra_layer_checkboxes.items():
        assert checkbox.isEnabled() is True, f"{name} checkbox should be a real, enabled toggle"
        assert checkbox.isChecked() is False  # off by default, same convention as before

        checkbox.setChecked(True)
        contour = panel._extra_layer_contours[name]
        assert contour.get_visible() is True

        checkbox.setChecked(False)
        assert contour.get_visible() is False


def test_extra_layer_contours_are_lazily_built_not_all_up_front(qtbot):
    """Real performance regression guard (added 2026-09-03, profiled
    AWCIDashboard.refresh()): update_data() must not build a real
    matplotlib contourf artist for a layer nobody has checked - that
    real construction cost (~4ms each) was previously paid on every
    single redraw for layers that were never shown."""
    panel = AWCIMapPanel("AWCI GLOBAL MAP", show_layers_panel=True)
    qtbot.addWidget(panel)  # every extra layer starts unchecked

    assert panel._extra_layer_contours == {}
    assert panel._last_layer_grids is not None  # the real grid itself is still computed


def test_checking_a_layer_lazily_builds_its_own_real_contour(qtbot):
    panel = AWCIMapPanel("AWCI GLOBAL MAP", show_layers_panel=True)
    qtbot.addWidget(panel)
    assert "Icing" not in panel._extra_layer_contours

    panel.extra_layer_checkboxes["Icing"].setChecked(True)

    assert "Icing" in panel._extra_layer_contours
    assert panel._extra_layer_contours["Icing"].get_visible() is True


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


# ------------------------------- city labels / CAPE checkbox / set_extent (dashboard parity)


def test_city_labels_empty_by_default(qtbot):
    panel = AWCIMapPanel("AWCI REGIONAL MAP")
    qtbot.addWidget(panel)
    assert panel._city_labels == []


def test_set_city_labels_stores_the_real_supplied_cities(qtbot):
    panel = AWCIMapPanel("AWCI REGIONAL MAP")
    qtbot.addWidget(panel)
    cities = [(36.8065, 10.1815, "Tunis")]

    panel.set_city_labels(cities)

    assert panel._city_labels == cities


def test_set_city_labels_does_not_raise_when_drawn(qtbot):
    panel = AWCIMapPanel("AWCI REGIONAL MAP")
    qtbot.addWidget(panel)
    panel.set_city_labels([(36.8065, 10.1815, "Tunis")])  # must not raise


def test_cape_checkbox_exists_and_is_a_real_working_toggle(qtbot):
    panel = AWCIMapPanel("AWCI GLOBAL MAP", show_layers_panel=True)
    qtbot.addWidget(panel)
    assert "CAPE" in panel.extra_layer_checkboxes
    assert panel.extra_layer_checkboxes["CAPE"].isEnabled() is True


def test_ceiling_visibility_dust_checkboxes_exist_and_are_real_working_toggles(qtbot):
    """2026-09-12 addition - same real, working-toggle guard as CAPE's
    own test above."""
    panel = AWCIMapPanel("AWCI GLOBAL MAP", show_layers_panel=True)
    qtbot.addWidget(panel)
    for name in ("Ceiling", "Visibility", "Dust"):
        assert name in panel.extra_layer_checkboxes
        assert panel.extra_layer_checkboxes[name].isEnabled() is True


def test_ceiling_uses_a_reversed_colormap_unlike_every_other_layer(qtbot):
    """Real, disclosed design choice: ceiling is the one layer here
    where a LOWER value is more hazardous - see _EXTRA_LAYER_SPECS'
    own NOTE for why it alone gets a reversed colormap."""
    panel = AWCIMapPanel("AWCI GLOBAL MAP", show_layers_panel=True)
    key, cmap, _tooltip = panel._EXTRA_LAYER_SPECS["Ceiling"]
    assert key == "ceiling"
    assert cmap.endswith("_r")
    for name in ("Wind", "Turbulence", "Icing", "Convection", "CAPE", "Clouds", "Visibility", "Dust"):
        _key, other_cmap, _tooltip = panel._EXTRA_LAYER_SPECS[name]
        assert not other_cmap.endswith("_r"), f"{name} was not expected to use a reversed colormap"


def test_ceiling_visibility_dust_are_real_in_real_physics_mode_too(qtbot):
    """Unlike Convection/CAPE/Clouds (demo mode only), ceiling/
    visibility/dust only need temperature/specific humidity/pressure/
    wind speed - all real and already available in Real Physics
    mode's own volume (see real_layer_grids_at_level()'s own
    docstring) - so checking them there must genuinely build a real
    contour, not silently no-op."""
    from acf.awci.path_sampling import real_layer_grids_at_level
    from acf.awci.vertical_field import compute_real_complexity_volume

    panel = AWCIMapPanel("AWCI GLOBAL MAP", show_layers_panel=True)
    qtbot.addWidget(panel)
    volume = compute_real_complexity_volume(model="ALADIN", n_lat=8, n_lon=12, n_levels=6, steps=2, seed=3)
    # set_external_field() must be called too (real production sequence
    # - see awci_dashboard.py's own _apply_volume_at_level()) for
    # update_data() to actually take its Real Physics branch at all;
    # set_external_layer_grids() alone leaves self._external_field
    # None, silently falling back to the demo-mode branch instead.
    panel.set_external_field(volume["lons"], volume["lats"], volume["awci_volume"][0], "REAL PHYSICS")
    panel.set_external_layer_grids(real_layer_grids_at_level(volume, level_idx=0))

    for name in ("Ceiling", "Visibility", "Dust"):
        panel.extra_layer_checkboxes[name].setChecked(True)
        assert name in panel._extra_layer_contours, f"{name} should have built a real contour in Real Physics mode"


def test_ceiling_visibility_dust_survive_a_real_data_refresh_in_real_physics_mode(qtbot):
    """Real regression guard (2026-09-12): update_data()'s own Real
    Physics rebuild branch used to hardcode ("Wind", "Turbulence",
    "Icing") - a real redraw (e.g. the flight-level slider) while
    Ceiling/Visibility/Dust was checked silently dropped its contour,
    since self._extra_layer_contours is rebuilt from scratch on every
    update_data() call. Same real bug class as
    test_layers_panel_state_survives_a_real_data_refresh above, for
    Real Physics mode specifically."""
    from acf.awci.path_sampling import real_layer_grids_at_level
    from acf.awci.vertical_field import compute_real_complexity_volume

    panel = AWCIMapPanel("AWCI GLOBAL MAP", show_layers_panel=True)
    qtbot.addWidget(panel)
    volume = compute_real_complexity_volume(model="ALADIN", n_lat=8, n_lon=12, n_levels=6, steps=2, seed=3)
    panel.set_external_field(volume["lons"], volume["lats"], volume["awci_volume"][0], "REAL PHYSICS")
    panel.set_external_layer_grids(real_layer_grids_at_level(volume, level_idx=0))
    panel.extra_layer_checkboxes["Ceiling"].setChecked(True)
    assert "Ceiling" in panel._extra_layer_contours

    panel.update_data(flight_level_hpa=500.0, time_offset_hours=3.0)

    assert "Ceiling" in panel._extra_layer_contours, "Ceiling's real contour must survive a real data refresh"


def test_set_extent_applies_to_the_real_camera(qtbot):
    """MapCamera.set_extent() derives its own real zoom_level/center
    from the request (see that class's own documented formula) - the
    resulting extent is not always bit-identical to the request, but
    must genuinely zoom in on (roughly centered on) the requested
    region, and change from the panel's own default whole-world view."""
    panel = AWCIMapPanel("AWCI GLOBAL MAP")
    qtbot.addWidget(panel)
    default_extent = panel.camera.current_extent()

    panel.set_extent(-12.0, 15.0, 25.0, 40.0)

    west, east, south, north = panel.camera.current_extent()
    assert (west, east, south, north) != default_extent
    assert abs(((west + east) / 2.0) - 1.5) < 5.0  # real center lon ~= (-12+15)/2
    assert abs(((south + north) / 2.0) - 32.5) < 5.0  # real center lat ~= (25+40)/2
    assert (east - west) < 180.0  # genuinely zoomed in, not still the whole world


def test_set_extent_does_not_trigger_a_full_data_redraw(qtbot):
    """Real regression guard: set_extent() must be the cheap camera-only
    path (like zoom_in/zoom_out), not a full update_data() rebuild."""
    panel = AWCIMapPanel("AWCI GLOBAL MAP")
    qtbot.addWidget(panel)
    contour_before = panel._contour

    panel.set_extent(-12.0, 15.0, 25.0, 40.0)

    assert panel._contour is contour_before
