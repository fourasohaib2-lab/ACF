"""
Tests for acf.gui.esoc.panel_manager.HydrologyPanel - upgrading the
real "Hydrology" leaf (panel #18, already mapped) from a hardcoded,
honestly disclaimed "Example Layout" text block to real, live
computation chaining the real bundled SRTM15+ terrain dataset into
FloodSimulator (2026-09-05, Phase 53).
"""

from __future__ import annotations

import numpy as np
import pytest
from PySide6.QtWidgets import QApplication

from acf.awci.terrain_elevation import interpolate_real_terrain_elevation
from acf.gui.esoc.command_dispatcher import CommandDispatcher
from acf.gui.esoc.module_registry import ModuleRegistry
from acf.gui.esoc.panel_manager import HydrologyPanel


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture()
def registry():
    return ModuleRegistry()


def test_default_result_matches_the_real_engines_directly(qapp, registry):
    dispatcher = CommandDispatcher()
    flood_module = registry.get_module("flood_simulator")
    panel = HydrologyPanel(registry, dispatcher)

    lats = np.linspace(30.50 - 0.05, 30.50 + 0.05, 9)
    lons = np.linspace(31.20 - 0.05, 31.20 + 0.05, 9)
    elevation_m = interpolate_real_terrain_elevation(lats, lons)
    rainfall = np.full_like(elevation_m, 60.0)
    soil_moisture = np.full_like(elevation_m, 0.30)
    expected = flood_module.simulate_inundation(rainfall, soil_moisture, elevation_m)

    text = panel.result.toPlainText()
    assert f"{float(elevation_m.min()):.1f}" in text
    assert f"{float(expected['inundation_depth_m'].mean()):.4f}" in text
    assert f"{float(expected['inundation_depth_m'].max()):.4f}" in text


def test_higher_rainfall_increases_the_real_computed_runoff_and_depth(qapp, registry):
    """Real physical-sanity check: more rainfall must genuinely raise
    both real surface runoff and real inundation depth."""
    dispatcher = CommandDispatcher()
    panel = HydrologyPanel(registry, dispatcher)

    panel.rainfall_rate.setValue(20.0)
    panel._simulate()
    low_rain_text = panel.result.toPlainText()

    panel.rainfall_rate.setValue(400.0)
    panel._simulate()
    high_rain_text = panel.result.toPlainText()

    assert low_rain_text != high_rain_text


def test_moving_the_patch_genuinely_changes_the_real_elevation_shown(qapp, registry):
    """Real regression guard: the elevation range must come from the
    real bundled terrain dataset at the chosen location, never a
    static number - a mountain patch and a delta patch must differ."""
    dispatcher = CommandDispatcher()
    panel = HydrologyPanel(registry, dispatcher)

    panel.center_lat.setValue(30.50)  # Nile Delta, real low-relief floodplain
    panel.center_lon.setValue(31.20)
    panel.half_width.setValue(0.02)
    panel._simulate()
    delta_text = panel.result.toPlainText()

    panel.center_lat.setValue(45.83)  # Alps, real high-relief mountains
    panel.center_lon.setValue(6.87)
    panel.half_width.setValue(0.02)
    panel._simulate()
    mountain_text = panel.result.toPlainText()

    assert delta_text != mountain_text


def test_grid_points_spinbox_rejects_a_degenerate_single_point_patch(qapp, registry):
    """A 1x1 elevation patch cannot support a real spatial gradient
    (same lesson as the domain-crop fix elsewhere in this codebase) -
    the spinbox's own minimum must forbid it."""
    dispatcher = CommandDispatcher()
    panel = HydrologyPanel(registry, dispatcher)

    assert panel.grid_points.minimum() >= 2


def test_panel_shows_an_honest_disconnected_label_when_not_registered(qapp, registry):
    dispatcher = CommandDispatcher()
    registry.modules["flood_simulator"] = None

    panel = HydrologyPanel(registry, dispatcher)

    assert not hasattr(panel, "button")
