"""
Tests for AWCIDashboard's "Real Physics" mode (src/acf/gui/dashboard/
awci_dashboard.py, added 2026-09-02, explicit user request "vas-y,
branche le dashboard").

The background-thread plumbing (QThreadPool/_RealFieldWorker) is
standard, trusted Qt machinery - these tests exercise the actual new
logic (_on_real_physics_ready()/_revert_to_demo()) directly with a
real compute_real_complexity_field() result (small grid override for
speed), the same way a completed worker signal would deliver it.
"""

import pytest
from PySide6.QtWidgets import QApplication

from acf.awci.spatial_field import compute_real_complexity_field
from acf.gui.dashboard.awci_dashboard import AWCIDashboard
from acf.gui.dashboard.awci_map_panel import AWCIMapPanel


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_dashboard_starts_in_demo_mode(qapp):
    dashboard = AWCIDashboard()
    assert dashboard._real_physics_active is False
    assert "Real Physics" in dashboard.real_physics_button.text()


def test_real_physics_ready_switches_to_real_mode_and_updates_panels(qapp):
    dashboard = AWCIDashboard()
    result = compute_real_complexity_field(model="ALADIN", n_lat=8, n_lon=14, n_levels=4, steps=3)

    dashboard._on_real_physics_ready(result)

    assert dashboard._real_physics_active is True
    assert "Back to Demo" in dashboard.real_physics_button.text()
    assert "REAL PHYSICS" in dashboard.real_physics_status.text()
    assert dashboard.global_map._external_field is not None
    assert dashboard.stats_bar.model_box.value_lbl.text() == "CoupledEarthSolver"
    # component_list must have real, non-placeholder module scores now
    # (not the "—" default from before any real point was computed).
    assert dashboard.component_list._values["convective"].text() != "—"
    assert dashboard.risk_summary._rows["physical"][1].text() != "—"


def test_revert_to_demo_restores_synthetic_state(qapp):
    dashboard = AWCIDashboard()
    result = compute_real_complexity_field(model="ALADIN", n_lat=8, n_lon=14, n_levels=4, steps=3)
    dashboard._on_real_physics_ready(result)

    dashboard._revert_to_demo()

    assert dashboard._real_physics_active is False
    assert "Real Physics" in dashboard.real_physics_button.text()
    assert dashboard.global_map._external_field is None
    assert dashboard.stats_bar.model_box.value_lbl.text() == "ACF Demo Grid"


def test_real_physics_failure_reports_the_error_and_stays_in_demo_mode(qapp):
    dashboard = AWCIDashboard()
    dashboard.real_physics_button.setEnabled(False)

    dashboard._on_real_physics_failed("boom")

    assert dashboard._real_physics_active is False
    assert dashboard.real_physics_button.isEnabled() is True
    assert "failed" in dashboard.real_physics_status.text().lower()


def test_map_panel_external_field_round_trip(qapp):
    panel = AWCIMapPanel("TEST MAP")
    result = compute_real_complexity_field(model="ALADIN", n_lat=6, n_lon=10, n_levels=4, steps=2)

    panel.set_external_field(result["lons"], result["lats"], result["awci_field"], "REAL PHYSICS")
    assert panel._external_field is not None
    assert "REAL PHYSICS" in panel._title

    panel.clear_external_field()
    assert panel._external_field is None
    assert panel._title == panel._base_title
