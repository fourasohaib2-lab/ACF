"""
GUI-level tests for acf.gui.dashboard.acf_workstation_convection.
ACFConvectionLabPanel - the real on-demand convective-indices button
wiring (the pure field function itself is covered by
tests/test_acf_workstation_convection.py).
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.awci.vertical_field import compute_real_complexity_volume
from acf.gui.dashboard.acf_workstation_convection import ACFConvectionLabPanel


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _real_small_volume(**overrides):
    # Small and coarse - real CAPE/CIN cost (~5ms/real MetPy parcel
    # ascent) must stay fast in a test even with stride=1 on this tiny
    # grid (4x4 -> 16 real points), same convention as this codebase's
    # own Thermodynamics Lab CAPE/CIN GUI tests.
    kwargs = dict(model="ALADIN", n_lat=4, n_lon=4, n_levels=6, steps=2, perturbation_scale=2.0, seed=1)
    kwargs.update(overrides)
    return compute_real_complexity_volume(**kwargs)


def test_starts_with_no_result_and_disabled_variable_selector(qapp):
    panel = ACFConvectionLabPanel()
    assert panel._volume is None
    assert panel._result is None
    assert panel.variable_selector.isEnabled() is False
    assert "Not yet computed" in panel.status_label.text()


def test_variable_selector_lists_the_8_real_composite_indices(qapp):
    panel = ACFConvectionLabPanel()
    names = [panel.variable_selector.itemText(i) for i in range(panel.variable_selector.count())]
    assert any("CAPE" in n for n in names)
    assert any("CIN" in n for n in names)
    assert any("LCL" in n for n in names)
    assert any("shear" in n for n in names)
    assert any("helicity" in n for n in names)
    assert any("Energy helicity index" in n for n in names)
    assert any("Supercell composite" in n for n in names)
    assert any("Significant tornado" in n for n in names)


def test_update_from_volume_is_real_bookkeeping_only(qapp):
    """Same "stays whatever it was" convention as Thermodynamics Lab's
    own CAPE/CIN - a level change never resets an already-computed
    on-demand full-column result."""
    panel = ACFConvectionLabPanel()
    volume = _real_small_volume()

    panel.update_from_volume(volume, level_index=0)

    assert panel._volume is volume
    assert panel._result is None  # bookkeeping only, no map drawn yet


def test_run_button_without_a_volume_reports_an_honest_error(qapp):
    panel = ACFConvectionLabPanel()

    panel._start_convection()

    assert "Run the Workstation" in panel.status_label.text()


def test_clicking_run_genuinely_runs_off_thread_and_populates_the_map(qtbot):
    """Drives the actual QThreadPool.globalInstance().start() + Qt
    event loop path, not a direct call - same discipline as
    test_acf_workstation_thermodynamics.py's own real-worker test."""
    panel = ACFConvectionLabPanel()
    qtbot.addWidget(panel)
    panel.update_from_volume(_real_small_volume(), level_index=0)

    panel.run_button.click()

    qtbot.waitUntil(lambda: panel._result is not None, timeout=30000)
    assert panel.variable_selector.isEnabled() is True
    assert "✅" in panel.status_label.text()
    assert panel.map_panel.status()["has_contour"] is True


def test_switching_variable_redraws_with_a_different_real_field(qtbot):
    panel = ACFConvectionLabPanel()
    qtbot.addWidget(panel)
    panel.update_from_volume(_real_small_volume(), level_index=0)
    panel.run_button.click()
    qtbot.waitUntil(lambda: panel._result is not None, timeout=30000)
    first_label = panel.map_panel._external_field_colorbar_label

    panel.variable_selector.setCurrentText("CIN (convective inhibition)")

    assert panel.map_panel._external_field_colorbar_label != first_label
    assert "CIN" in panel.map_panel._external_field_colorbar_label


def test_convective_result_is_not_reset_by_a_level_change(qtbot):
    """Same real "not tied to the level slider" convention already
    documented on Thermodynamics Lab's own CAPE/CIN - these are all
    real full-column diagnostics."""
    panel = ACFConvectionLabPanel()
    qtbot.addWidget(panel)
    volume = _real_small_volume()
    panel.update_from_volume(volume, level_index=0)
    panel.run_button.click()
    qtbot.waitUntil(lambda: panel._result is not None, timeout=30000)
    result_before = panel._result

    panel.update_from_volume(volume, level_index=volume["n_levels"] - 1)

    assert panel._result is result_before
