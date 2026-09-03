"""
Tests for AWCIDashboard's "Real Physics" mode (src/acf/gui/dashboard/
awci_dashboard.py, added 2026-09-02, explicit user request "vas-y,
branche le dashboard", extended the same day to "branche la carte
régionale/coupe/route sur les vrais champs").

The background-thread plumbing (QThreadPool/_RealFieldWorker) is
standard, trusted Qt machinery - these tests exercise the actual new
logic (_on_real_physics_ready()/_revert_to_demo()) directly with a
real compute_real_complexity_volume() result (small grid override for
speed), the same way a completed worker signal would deliver it.
"""

import pytest
from PySide6.QtWidgets import QApplication

from acf.awci.vertical_field import compute_real_complexity_volume
from acf.gui.dashboard.awci_dashboard import AWCIDashboard
from acf.gui.dashboard.awci_map_panel import AWCIMapPanel


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _real_volume(**overrides):
    kwargs = dict(model="ALADIN", n_lat=10, n_lon=18, n_levels=5, steps=3, perturbation_scale=2.0, seed=1)
    kwargs.update(overrides)
    return compute_real_complexity_volume(**kwargs)


def test_dashboard_starts_in_demo_mode(qapp):
    dashboard = AWCIDashboard()
    assert dashboard._real_physics_active is False
    assert "Real Physics" in dashboard.real_physics_button.text()


def test_real_physics_ready_switches_to_real_mode_and_updates_panels(qapp):
    dashboard = AWCIDashboard()
    volume = _real_volume()

    dashboard._on_real_physics_ready(volume)

    assert dashboard._real_physics_active is True
    assert "Back to Demo" in dashboard.real_physics_button.text()
    assert "REAL PHYSICS" in dashboard.real_physics_status.text()
    assert dashboard.global_map._external_field is not None
    assert dashboard.stats_bar.model_box.value_lbl.text() == "CoupledEarthSolver"
    assert dashboard.component_list._rows["convective"].value_label.text() != "—"
    assert dashboard.risk_summary._rows["physical"][1].text() != "—"


def test_real_physics_ready_wires_route_and_cross_section_too(qapp):
    """Explicit request: regional map, route chart and cross-section must ALSO be sampled from the real volume."""
    dashboard = AWCIDashboard()
    volume = _real_volume()

    dashboard._on_real_physics_ready(volume)

    assert dashboard.route_chart._external_route is not None
    assert dashboard.cross_section._external_cross_section is not None
    distances_km, scores = dashboard.route_chart._external_route
    assert len(distances_km) == len(scores) == 40


def test_real_physics_ready_wires_regional_map_when_grid_is_fine_enough(qapp):
    """A finer real grid (AROME-scale override) should have >= 2x2 real points inside the regional extent -> regional map gets wired."""
    dashboard = AWCIDashboard()
    volume = _real_volume(n_lat=40, n_lon=80)

    dashboard._on_real_physics_ready(volume)

    assert dashboard.regional_map._external_field is not None


def test_real_physics_ready_leaves_regional_map_synthetic_when_grid_too_coarse(qapp):
    """A very coarse real grid should fall back to the synthetic regional map rather than crash or show a broken plot."""
    dashboard = AWCIDashboard()
    volume = _real_volume(n_lat=3, n_lon=5)  # too coarse for North Africa's extent

    dashboard._on_real_physics_ready(volume)

    assert dashboard.regional_map._external_field is None


def test_revert_to_demo_restores_synthetic_state(qapp):
    dashboard = AWCIDashboard()
    volume = _real_volume()
    dashboard._on_real_physics_ready(volume)

    dashboard._revert_to_demo()

    assert dashboard._real_physics_active is False
    assert "Real Physics" in dashboard.real_physics_button.text()
    assert dashboard.global_map._external_field is None
    assert dashboard.regional_map._external_field is None
    assert dashboard.route_chart._external_route is None
    assert dashboard.cross_section._external_cross_section is None
    assert dashboard.stats_bar.model_box.value_lbl.text() == "ACF Demo Grid"


def test_real_physics_failure_reports_the_error_and_stays_in_demo_mode(qapp):
    dashboard = AWCIDashboard()
    dashboard.real_physics_button.setEnabled(False)

    dashboard._on_real_physics_failed("boom")

    assert dashboard._real_physics_active is False
    assert dashboard.real_physics_button.isEnabled() is True
    assert "failed" in dashboard.real_physics_status.text().lower()


def test_on_real_physics_ready_would_catch_a_reintroduced_lat_lon_swap(qapp, monkeypatch):
    """
    Real regression guard (added 2026-09-02): this exact code path once
    had lons/lats swapped (see git history) - a PhysicsGuard coordinate
    check was added at the exact line it happened. This test proves
    the guard is genuinely wired in and would raise if that bug ever
    came back, by forcing the swap via a monkeypatched volume dict.
    """
    from acf.core.exceptions import CoordinateError

    dashboard = AWCIDashboard()
    volume = _real_volume()
    swapped_volume = {**volume, "lats": volume["lons"], "lons": volume["lats"]}

    with pytest.raises(CoordinateError):
        dashboard._on_real_physics_ready(swapped_volume)


def test_map_panel_external_field_round_trip(qapp):
    panel = AWCIMapPanel("TEST MAP")
    volume = _real_volume()

    panel.set_external_field(volume["lons"], volume["lats"], volume["awci_volume"][0], "REAL PHYSICS")
    assert panel._external_field is not None
    assert "REAL PHYSICS" in panel._title

    panel.clear_external_field()
    assert panel._external_field is None
    assert panel._title == panel._base_title
