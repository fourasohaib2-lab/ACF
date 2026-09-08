"""
GUI-level tests for acf.gui.dashboard.acf_workstation_thermodynamics.
ACFThermodynamicsLabPanel - the real on-demand CAPE/CIN button wiring
(the pure helper functions themselves are covered by
tests/test_acf_workstation_thermodynamics.py).
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.awci.vertical_field import compute_real_complexity_volume
from acf.gui.dashboard.acf_workstation_thermodynamics import ACFThermodynamicsLabPanel


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _real_small_volume(**overrides):
    # Small and coarse - real CAPE/CIN cost (~5ms/real MetPy parcel
    # ascent) must stay fast in a test even with stride=1 on this tiny
    # grid (4x4 -> 16 real points).
    kwargs = dict(model="ALADIN", n_lat=4, n_lon=4, n_levels=6, steps=2, perturbation_scale=2.0, seed=1)
    kwargs.update(overrides)
    return compute_real_complexity_volume(**kwargs)


def test_starts_with_no_volume_and_disabled_cape_selector(qapp):
    panel = ACFThermodynamicsLabPanel()
    assert panel._volume is None
    assert panel.cape_variable_selector.isEnabled() is False
    assert "Not yet computed" in panel.cape_status_label.text()


def test_variable_selector_lists_theta_e_and_relative_humidity(qapp):
    panel = ACFThermodynamicsLabPanel()
    names = [panel.variable_selector.itemText(i) for i in range(panel.variable_selector.count())]
    assert any("θ-e" in n or "potential temperature" in n for n in names)
    assert any("Relative humidity" in n for n in names)


def test_update_from_volume_redraws_the_auto_map(qapp):
    panel = ACFThermodynamicsLabPanel()
    volume = _real_small_volume()

    panel.update_from_volume(volume, level_index=0)

    assert panel._volume is volume
    assert panel.map_panel.status()["has_contour"] is True
    assert panel.map_panel._external_field is not None


def test_cape_button_without_a_volume_reports_an_honest_error(qapp):
    panel = ACFThermodynamicsLabPanel()

    panel._start_cape_cin()

    assert "Run the Workstation" in panel.cape_status_label.text()


def test_clicking_cape_button_genuinely_runs_off_thread_and_populates_the_map(qtbot):
    """Drives the actual QThreadPool.globalInstance().start() + Qt
    event loop path, not a direct call - same discipline as
    test_acf_workstation.py's own real-worker test."""
    panel = ACFThermodynamicsLabPanel()
    qtbot.addWidget(panel)
    panel.update_from_volume(_real_small_volume(), level_index=0)

    panel.cape_button.click()

    qtbot.waitUntil(lambda: panel._cape_grid is not None, timeout=30000)
    assert panel.cape_variable_selector.isEnabled() is True
    assert "✅" in panel.cape_status_label.text()
    assert panel.cape_map.status()["has_contour"] is True


def test_cape_cin_result_is_not_reset_by_a_level_change(qtbot):
    """Same real "not tied to the level slider" convention already
    documented on Complexity Explorer's own temporal/consensus
    dimensions - CAPE/CIN is a full-column diagnostic."""
    panel = ACFThermodynamicsLabPanel()
    qtbot.addWidget(panel)
    volume = _real_small_volume()
    panel.update_from_volume(volume, level_index=0)
    panel.cape_button.click()
    qtbot.waitUntil(lambda: panel._cape_grid is not None, timeout=30000)
    cape_grid_before = panel._cape_grid

    panel.update_from_volume(volume, level_index=volume["n_levels"] - 1)

    assert panel._cape_grid is cape_grid_before
