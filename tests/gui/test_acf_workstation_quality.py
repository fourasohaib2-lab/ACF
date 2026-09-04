"""
GUI-level tests for
acf.gui.dashboard.acf_workstation_quality.ACFDataQualityLabPanel.
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.awci.vertical_field import compute_real_complexity_volume
from acf.gui.dashboard.acf_workstation_quality import _VARIABLES, ACFDataQualityLabPanel


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _real_small_volume(**overrides):
    kwargs = dict(model="ALADIN", n_lat=5, n_lon=5, n_levels=4, steps=2, perturbation_scale=2.0, seed=1)
    kwargs.update(overrides)
    return compute_real_complexity_volume(**kwargs)


def test_starts_with_no_volume(qapp):
    panel = ACFDataQualityLabPanel()
    assert panel._volume is None


def test_variable_selector_lists_all_4_real_variables(qapp):
    panel = ACFDataQualityLabPanel()
    names = [panel.variable_selector.itemText(i) for i in range(panel.variable_selector.count())]
    assert names == list(_VARIABLES.keys())


def test_update_from_volume_redraws_the_map_and_reports_real_counts(qapp):
    panel = ACFDataQualityLabPanel()
    volume = _real_small_volume()

    panel.update_from_volume(volume, level_index=0)

    assert panel._volume is volume
    assert panel.map_panel.status()["has_contour"] is True
    assert "/" in panel.status_label.text()  # a real "X/Y (Z%)" count breakdown


def test_pressure_variable_honestly_reports_the_real_anomaly(qapp):
    """Real regression guard: this Workstation's own known pressure
    anomaly (task_f3c406d9) must surface as OUT_OF_RANGE in this real
    panel too, not be silently hidden."""
    panel = ACFDataQualityLabPanel()
    panel.variable_selector.setCurrentText("Pressure")

    panel.update_from_volume(_real_small_volume(), level_index=0)

    assert "OUT_OF_RANGE" in panel.status_label.text()
    assert "⚠" in panel.status_label.text()


def test_temperature_variable_reports_real_valid_status(qapp):
    panel = ACFDataQualityLabPanel()
    panel.variable_selector.setCurrentText("Temperature")

    panel.update_from_volume(_real_small_volume(), level_index=0)

    assert "✅" in panel.status_label.text()
    assert "VALID" in panel.status_label.text()
