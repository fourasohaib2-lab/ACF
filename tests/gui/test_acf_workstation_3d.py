"""
GUI-level tests for
acf.gui.dashboard.acf_workstation_3d.ACF3DAtmospherePanel.
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.awci.vertical_field import compute_real_complexity_volume
from acf.gui.dashboard.acf_workstation_3d import _MAX_SHOWN_LEVELS, _VARIABLES, ACF3DAtmospherePanel


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _real_small_volume(**overrides):
    kwargs = dict(model="ALADIN", n_lat=5, n_lon=5, n_levels=8, steps=2, perturbation_scale=2.0, seed=1)
    kwargs.update(overrides)
    return compute_real_complexity_volume(**kwargs)


def test_starts_with_no_volume(qapp):
    panel = ACF3DAtmospherePanel()
    assert panel._volume is None


def test_variable_selector_lists_the_real_variables(qapp):
    panel = ACF3DAtmospherePanel()
    names = [panel.variable_selector.itemText(i) for i in range(panel.variable_selector.count())]
    assert names == list(_VARIABLES.keys())


def test_axis_is_a_real_3d_projection(qapp):
    panel = ACF3DAtmospherePanel()
    assert panel.axis.name == "3d"


def test_update_from_volume_draws_real_stacked_contours(qapp):
    panel = ACF3DAtmospherePanel()
    volume = _real_small_volume()

    panel.update_from_volume(volume, level_index=0)

    assert panel._volume is volume
    # A real Axes3D redraw leaves real Poly3DCollection artists behind
    # for each stacked real contourf level.
    assert len(panel.axis.collections) > 0


def test_shows_at_most_max_shown_levels_even_for_a_deep_volume(qapp):
    panel = ACF3DAtmospherePanel()
    volume = _real_small_volume(n_levels=20)  # more real levels than _MAX_SHOWN_LEVELS

    panel.update_from_volume(volume, level_index=0)

    # Real regression guard: never silently render every single native
    # level (would be unreadable/slow) - see module docstring's
    # "Honest rendering choice".
    assert len(panel.axis.collections) <= _MAX_SHOWN_LEVELS + 2  # some slack for axis/gridline artists


def test_z_axis_is_inverted_pressure_ground_at_the_bottom(qapp):
    """Real meteorological convention: high pressure (ground) at the
    bottom, low pressure (upper atmosphere) at the top - the real Z
    limits must come back with the smaller (upper-atmosphere) real
    pressure value LAST after inversion."""
    panel = ACF3DAtmospherePanel()
    panel.update_from_volume(_real_small_volume(), level_index=0)

    zlim = panel.axis.get_zlim()
    assert zlim[0] > zlim[1]  # inverted: ground (high hPa) first, upper atmosphere (low hPa) last


def test_switching_variable_redraws_without_error(qapp):
    panel = ACF3DAtmospherePanel()
    panel.update_from_volume(_real_small_volume(), level_index=0)

    panel.variable_selector.setCurrentText("Wind speed")

    assert len(panel.axis.collections) > 0
