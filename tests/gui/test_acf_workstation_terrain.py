"""
GUI-level tests for acf.gui.dashboard.acf_workstation_terrain.
ACFTerrainLabPanel - the real auto-rendered terrain elevation / static
stability / mountain-wave Froude number panel (the pure field function
itself is covered by tests/test_acf_workstation_terrain.py).
"""

from __future__ import annotations

import numpy as np
import pytest
from PySide6.QtWidgets import QApplication

from acf.awci.vertical_field import compute_real_complexity_volume
from acf.gui.dashboard.acf_workstation_terrain import ACFTerrainLabPanel


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _real_small_volume(**overrides):
    kwargs = dict(model="ALADIN", n_lat=6, n_lon=6, n_levels=4, steps=2, perturbation_scale=2.0, seed=1)
    kwargs.update(overrides)
    return compute_real_complexity_volume(**kwargs)


def test_starts_with_no_result(qapp):
    panel = ACFTerrainLabPanel()
    assert panel._volume is None
    assert panel._result is None


def test_variable_selector_lists_the_3_real_fields(qapp):
    panel = ACFTerrainLabPanel()
    names = [panel.variable_selector.itemText(i) for i in range(panel.variable_selector.count())]
    assert any("elevation" in n for n in names)
    assert any("Brunt-Väisälä" in n for n in names)
    assert any("Froude" in n for n in names)


def test_update_from_volume_genuinely_computes_the_real_terrain_field(qapp):
    """No on-demand button here (see module docstring for why this is
    cheap enough to auto-render) - update_from_volume() itself must
    produce a real, populated result synchronously."""
    panel = ACFTerrainLabPanel()
    volume = _real_small_volume()

    panel.update_from_volume(volume, level_index=0)

    assert panel._volume is volume
    assert panel._result is not None
    assert panel.map_panel.status()["has_contour"] is True
    assert panel.map_panel._external_field is not None


def test_switching_variable_redraws_with_a_different_real_field(qapp):
    panel = ACFTerrainLabPanel()
    panel.update_from_volume(_real_small_volume(), level_index=0)
    first_label = panel.map_panel._external_field_colorbar_label

    panel.variable_selector.setCurrentText("Mountain-wave Froude number")

    assert panel.map_panel._external_field_colorbar_label != first_label
    assert "Froude" in panel.map_panel._external_field_colorbar_label


def test_terrain_result_is_not_reset_by_a_pure_level_change_but_stays_real(qapp):
    """Elevation/static-stability/Froude are real, full-column,
    level-independent diagnostics (see module docstring) - a level
    change still recomputes (cheap enough, see that same docstring)
    but must keep producing a real, consistent result, not stale/broken
    state."""
    panel = ACFTerrainLabPanel()
    volume = _real_small_volume()
    panel.update_from_volume(volume, level_index=0)
    first_elevation = panel._result["elevation_m"].copy()

    panel.update_from_volume(volume, level_index=volume["n_levels"] - 1)

    assert panel._result is not None
    # Same real volume, same real elevation (level-independent) - must
    # be identical, not perturbed by the level change.
    assert np.array_equal(panel._result["elevation_m"], first_elevation)
