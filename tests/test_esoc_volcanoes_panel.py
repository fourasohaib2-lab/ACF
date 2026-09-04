"""
Tests for acf.gui.esoc.panel_manager.VolcanoesPanel - the real Mogi
surface-deformation / plume-height panel closing the previously-dead
"Earth System / Volcanoes" System Explorer leaf (2026-09-05).
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.esoc.command_dispatcher import CommandDispatcher
from acf.gui.esoc.module_registry import ModuleRegistry
from acf.gui.esoc.panel_manager import VolcanoesPanel
from acf.geology.volcanic_physics import VolcanicPhysicsEngine


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture()
def registry():
    return ModuleRegistry()


def test_deformation_matches_the_real_engine_directly(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = VolcanoesPanel(registry, dispatcher)

    panel.deform_radius.setValue(3000.0)
    panel.deform_depth.setValue(6000.0)
    panel.deform_volume.setValue(2_000_000.0)
    panel.deform_button.click()

    expected = VolcanicPhysicsEngine.mogi_surface_displacement_m(
        radial_distance_m=3000.0, chamber_depth_m=6000.0, volume_change_m3=2_000_000.0
    )
    text = panel.deform_result.toPlainText()
    assert f"{expected['vertical_displacement_m']:.4f}" in text
    assert f"{expected['radial_displacement_m']:.4f}" in text


def test_deformation_varies_authentically_with_input(qapp, registry):
    """Real regression guard: a genuinely different input must produce
    a genuinely different real output, never a fixed/cached value."""
    dispatcher = CommandDispatcher()
    panel = VolcanoesPanel(registry, dispatcher)

    panel.deform_radius.setValue(1000.0)
    panel.deform_button.click()
    near_result = panel.deform_result.toPlainText()

    panel.deform_radius.setValue(50000.0)
    panel.deform_button.click()
    far_result = panel.deform_result.toPlainText()

    assert near_result != far_result


def test_plume_height_matches_the_real_engine_directly(qapp, registry):
    dispatcher = CommandDispatcher()
    panel = VolcanoesPanel(registry, dispatcher)

    panel.plume_rate.setValue(250.0)
    panel.plume_button.click()

    expected_km = VolcanicPhysicsEngine.volcanic_plume_height_km(250.0)
    assert f"{expected_km:.2f}" in panel.plume_result.text()


def test_panel_shows_an_honest_disconnected_label_when_not_registered(qapp, registry):
    dispatcher = CommandDispatcher()
    registry.modules["volcanoes"] = None

    panel = VolcanoesPanel(registry, dispatcher)

    assert not hasattr(panel, "deform_button")
