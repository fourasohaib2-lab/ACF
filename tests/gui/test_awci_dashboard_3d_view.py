"""
Tests for AWCIDashboard's "🧊 3D View" button (explicit user request
"ajoute la 4eme dimension" - the real-3D half, alongside the level
slider in tests/gui/test_awci_dashboard_level_slider.py).
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


def test_3d_view_button_disabled_before_real_physics(qapp):
    dashboard = AWCIDashboard()
    assert dashboard.view_3d_button.isEnabled() is False


def test_3d_view_button_enabled_after_real_physics_ready(qapp):
    dashboard = AWCIDashboard()
    dashboard._on_real_physics_ready(_real_volume())
    assert dashboard.view_3d_button.isEnabled() is True


def test_opening_the_3d_view_populates_it_with_the_real_volume(qapp):
    dashboard = AWCIDashboard()
    volume = _real_volume()
    dashboard._on_real_physics_ready(volume)

    dashboard._open_3d_view()

    assert dashboard._volume_3d_window is not None
    assert dashboard._volume_3d_window.status()["has_data"] is True


def test_a_new_real_physics_run_refreshes_an_already_open_3d_view(qapp):
    dashboard = AWCIDashboard()
    dashboard._on_real_physics_ready(_real_volume(seed=1))
    dashboard._open_3d_view()
    first_title = dashboard._volume_3d_window._title

    dashboard._on_real_physics_ready(_real_volume(seed=2, n_levels=7))

    # Still populated (not reset to empty) and re-labeled from the new run.
    assert dashboard._volume_3d_window.status()["has_data"] is True
    assert dashboard._volume_3d_window._title == first_title  # same label text ("... — REAL PHYSICS")


def test_revert_to_demo_disables_the_button_and_clears_an_open_view(qapp):
    dashboard = AWCIDashboard()
    dashboard._on_real_physics_ready(_real_volume())
    dashboard._open_3d_view()

    dashboard._revert_to_demo()

    assert dashboard.view_3d_button.isEnabled() is False
    assert dashboard._volume_3d_window.status()["has_data"] is False
