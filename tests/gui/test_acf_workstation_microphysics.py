"""
GUI-level tests for
acf.gui.dashboard.acf_workstation_microphysics.ACFMicrophysicsLabPanel.
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.awci.vertical_field import compute_real_complexity_volume
from acf.gui.dashboard.acf_workstation_microphysics import ACFMicrophysicsLabPanel


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _real_small_volume(**overrides):
    kwargs = dict(model="ALADIN", n_lat=6, n_lon=6, n_levels=5, steps=2, perturbation_scale=2.0, seed=1)
    kwargs.update(overrides)
    return compute_real_complexity_volume(**kwargs)


def test_starts_with_no_volume(qapp):
    panel = ACFMicrophysicsLabPanel()
    assert panel._volume is None


def test_variable_selector_lists_phase_severity_and_wet_bulb(qapp):
    panel = ACFMicrophysicsLabPanel()
    names = [panel.variable_selector.itemText(i) for i in range(panel.variable_selector.count())]
    assert any("Precipitation phase severity" in n for n in names)
    assert any("Wet-bulb" in n for n in names)


def test_update_from_volume_redraws_the_map(qapp):
    panel = ACFMicrophysicsLabPanel()
    volume = _real_small_volume()

    panel.update_from_volume(volume, level_index=0)

    assert panel._volume is volume
    assert panel.map_panel.status()["has_contour"] is True
    assert panel.map_panel._external_field is not None


def test_switching_variable_redraws_with_a_different_real_field(qapp):
    panel = ACFMicrophysicsLabPanel()
    panel.update_from_volume(_real_small_volume(), level_index=0)
    first_label = panel.map_panel._external_field_colorbar_label

    panel.variable_selector.setCurrentText("Wet-bulb temperature")

    assert panel.map_panel._external_field_colorbar_label != first_label
    assert "Wet-bulb" in panel.map_panel._external_field_colorbar_label
