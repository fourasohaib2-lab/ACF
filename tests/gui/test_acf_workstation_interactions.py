"""
GUI-level tests for
acf.gui.dashboard.acf_workstation_interactions.ACFInteractionEnginePanel.
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.awci.vertical_field import compute_real_complexity_volume
from acf.gui.dashboard.acf_workstation_interactions import _VARIABLE_NAMES, ACFInteractionEnginePanel


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
    panel = ACFInteractionEnginePanel()
    assert panel._volume is None


def test_both_selectors_list_every_real_variable(qapp):
    panel = ACFInteractionEnginePanel()
    names_a = [panel.variable_a_selector.itemText(i) for i in range(panel.variable_a_selector.count())]
    names_b = [panel.variable_b_selector.itemText(i) for i in range(panel.variable_b_selector.count())]
    assert names_a == _VARIABLE_NAMES
    assert names_b == _VARIABLE_NAMES


def test_update_from_volume_redraws_the_map_and_reports_a_real_correlation(qapp):
    panel = ACFInteractionEnginePanel()
    # Temperature/Wind speed are both real, spatially-varying raw
    # fields on any real solver run - avoids the small test volume's
    # own real degenerate cases (e.g. relative humidity can be a real,
    # honestly-uniform 100% on a small/coarse test grid - see
    # test_switching_a_variable_redraws... below, which deliberately
    # picks these same 2 variables for the same reason).
    panel.variable_a_selector.setCurrentText("Temperature")
    panel.variable_b_selector.setCurrentText("Wind speed")
    volume = _real_small_volume()

    panel.update_from_volume(volume, level_index=0)

    assert panel._volume is volume
    assert panel.map_panel.status()["has_contour"] is True
    assert "Pearson r" in panel.status_label.text()


def test_switching_a_variable_redraws_with_a_different_real_field(qapp):
    panel = ACFInteractionEnginePanel()
    panel.update_from_volume(_real_small_volume(), level_index=0)
    first_label = panel.map_panel._external_field_colorbar_label

    panel.variable_a_selector.setCurrentText("Temperature")
    panel.variable_b_selector.setCurrentText("Wind speed")

    assert panel.map_panel._external_field_colorbar_label == first_label  # colorbar label is fixed (z-score units)
    assert "Temperature" in panel.map_panel._title
    assert "Wind speed" in panel.map_panel._title


def test_same_variable_on_both_sides_gives_a_perfect_real_correlation(qapp):
    """A real, trivial sanity case: a variable perfectly correlates
    with itself - real Pearson r must read +1.000."""
    panel = ACFInteractionEnginePanel()
    panel.variable_a_selector.setCurrentText("Temperature")
    panel.variable_b_selector.setCurrentText("Temperature")

    panel.update_from_volume(_real_small_volume(), level_index=0)

    assert "+1.000" in panel.status_label.text()
