"""
Tests for AWCIDashboard's "📊 Report" button and
AWCIExecutionReportDialog (docs/ACF_MASTER_PROMPT.md §75, explicit
user request "je veux rendre tout les boutons de awci en marche").
"""

import pytest
from PySide6.QtWidgets import QApplication

from acf.awci.vertical_field import compute_real_complexity_volume
from acf.gui.dashboard.awci_dashboard import AWCIDashboard


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _real_volume(**overrides):
    kwargs = dict(model="ALADIN", n_lat=8, n_lon=12, n_levels=6, steps=2, perturbation_scale=2.0, seed=1)
    kwargs.update(overrides)
    return compute_real_complexity_volume(**kwargs)


def test_dashboard_populates_real_quality_on_the_last_awci_result(qapp):
    """refresh() in __init__ already built one real point-of-interest
    result - it must carry real quality (§32), not None, now that
    _quality_for_point_raw_data() is wired in."""
    dashboard = AWCIDashboard()
    assert dashboard._last_awci_result is not None
    assert dashboard._last_awci_result.quality is not None
    assert set(dashboard._last_awci_result.quality.keys()) == {
        "air_temperature", "specific_humidity", "wind_speed", "air_pressure",
    }
    for status in dashboard._last_awci_result.quality.values():
        assert status.status == "VALID"


def test_real_physics_mode_also_populates_real_quality(qapp):
    dashboard = AWCIDashboard()
    dashboard._on_real_physics_ready(_real_volume())
    assert dashboard._last_awci_result.quality is not None
    assert len(dashboard._last_awci_result.quality) == 4


def test_clicking_report_button_opens_the_dialog(qapp):
    dashboard = AWCIDashboard()
    assert dashboard._execution_report_window is None

    dashboard.execution_report_button.click()

    assert dashboard._execution_report_window is not None
    assert dashboard._execution_report_window.isVisible()


def test_report_dialog_shows_the_real_current_result(qapp):
    dashboard = AWCIDashboard()
    dashboard._open_execution_report()

    rendered = [label.text() for label in dashboard._execution_report_window._row_labels]
    assert any(line.startswith("Quality:") for line in rendered)
    assert any("GOOD" in line for line in rendered)  # the default point-of-interest has all-VALID quality
    assert any(line.startswith("AWCI generated: YES") for line in rendered)


def test_clicking_report_reuses_the_same_dialog_instance(qapp):
    dashboard = AWCIDashboard()
    dashboard._open_execution_report()
    first = dashboard._execution_report_window
    dashboard._open_execution_report()
    assert dashboard._execution_report_window is first


def test_report_dialog_reflects_a_new_point_after_a_map_click(qapp):
    """The report must never show a stale point's data - clicking a
    new point of interest and reopening the report must reflect it."""
    dashboard = AWCIDashboard()
    dashboard.global_map.pointClicked.emit(10.0, 20.0)
    dashboard._open_execution_report()

    rendered = [label.text() for label in dashboard._execution_report_window._row_labels]
    assert any(line.startswith("Diagnostics:") for line in rendered)
    diagnostics_line = next(line for line in rendered if line.startswith("Diagnostics:"))
    expected = len(dashboard._last_awci_result.module_scores) + len(dashboard._last_awci_result.interaction_scores)
    assert diagnostics_line == f"Diagnostics: {expected}"
