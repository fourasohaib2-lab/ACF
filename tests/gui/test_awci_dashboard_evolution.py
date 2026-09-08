"""
Tests for AWCIDashboard's "▶ Play Evolution (4D)" real animation
(src/acf/gui/dashboard/awci_dashboard.py, explicit user request
"brancher l'animation 4D dans le dashboard").

Background-thread plumbing (_EvolutionWorker/QThreadPool) is the same
trusted pattern as _RealFieldWorker - these tests exercise the actual
new logic (_on_evolution_ready()/_advance_evolution_frame()/...)
directly with a real compute_real_complexity_evolution() result (small
grid override for speed), the same way a completed worker signal would
deliver it. QTimer.start()/stop()/isActive() work without a running
Qt event loop (isActive() just reflects whether start() was called
since the last stop()) - the timeout signal firing on its own isn't
needed since tests call _advance_evolution_frame() directly.
"""

import pytest
from PySide6.QtWidgets import QApplication

from acf.awci.temporal_field import compute_real_complexity_evolution
from acf.awci.vertical_field import compute_real_complexity_volume
from acf.gui.dashboard.awci_dashboard import AWCIDashboard


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


def _real_evolution(**overrides):
    kwargs = dict(
        model="ALADIN", n_lat=6, n_lon=10, n_levels=4, n_frames=4, steps_per_frame=2,
        perturbation_scale=2.0, seed=1,
    )
    kwargs.update(overrides)
    return compute_real_complexity_evolution(**kwargs)


def test_play_button_hidden_before_real_physics(qapp):
    dashboard = AWCIDashboard()
    assert dashboard.play_evolution_button.isVisible() is False


def test_play_button_visible_after_real_physics_ready(qapp):
    dashboard = AWCIDashboard()
    # isVisible() reflects EFFECTIVE visibility (whole parent chain
    # shown on screen), not just this widget's own setVisible(True)
    # flag - the dashboard must actually be shown for this assertion
    # to mean anything (found by a real failure, not assumed).
    dashboard.show()
    dashboard._on_real_physics_ready(_real_volume())
    assert dashboard.play_evolution_button.isVisible() is True
    assert dashboard.play_evolution_button.isEnabled() is True


def test_evolution_ready_starts_playback_and_renders_first_frame(qapp):
    dashboard = AWCIDashboard()
    dashboard._on_real_physics_ready(_real_volume())
    evolution = _real_evolution()

    dashboard._on_evolution_ready(evolution)

    assert dashboard._evolution is evolution
    assert dashboard._evolution_frame_index == 0
    assert dashboard._evolution_timer.isActive() is True
    assert "Stop Animation" in dashboard.play_evolution_button.text()
    assert dashboard.global_map._external_field is not None
    assert "REAL PHYSICS" in dashboard.global_map._title
    assert "t+" in dashboard.time_readout.text()


def test_advance_evolution_frame_wraps_around_real_frame_count(qapp):
    dashboard = AWCIDashboard()
    dashboard._on_real_physics_ready(_real_volume())
    evolution = _real_evolution(n_frames=4)
    dashboard._on_evolution_ready(evolution)

    seen_indices = [dashboard._evolution_frame_index]
    for _ in range(6):
        dashboard._advance_evolution_frame()
        seen_indices.append(dashboard._evolution_frame_index)

    assert max(seen_indices) < 4
    assert seen_indices == [0, 1, 2, 3, 0, 1, 2]


def test_advance_evolution_frame_uses_real_per_frame_values(qapp):
    dashboard = AWCIDashboard()
    dashboard._on_real_physics_ready(_real_volume())
    evolution = _real_evolution()
    dashboard._on_evolution_ready(evolution)

    dashboard._advance_evolution_frame()
    lons, lats, grid = dashboard.global_map._external_field
    import numpy as np

    np.testing.assert_array_equal(grid, evolution["awci_evolution"][1, 0])


def test_toggle_evolution_playback_stops_when_active(qapp):
    dashboard = AWCIDashboard()
    dashboard._on_real_physics_ready(_real_volume())
    dashboard._on_evolution_ready(_real_evolution())
    assert dashboard._evolution_timer.isActive() is True

    dashboard._toggle_evolution_playback()

    assert dashboard._evolution_timer.isActive() is False
    assert dashboard.play_evolution_button.text() == "▶ Play Evolution (4D)"


def test_toggle_evolution_playback_resumes_without_recomputing(qapp):
    dashboard = AWCIDashboard()
    dashboard._on_real_physics_ready(_real_volume())
    evolution = _real_evolution()
    dashboard._on_evolution_ready(evolution)
    dashboard._advance_evolution_frame()
    dashboard._advance_evolution_frame()
    dashboard._toggle_evolution_playback()  # stop
    assert dashboard._evolution_timer.isActive() is False

    dashboard._toggle_evolution_playback()  # resume

    assert dashboard._evolution is evolution  # same object - not recomputed
    assert dashboard._evolution_frame_index == 0  # restarted from frame 0
    assert dashboard._evolution_timer.isActive() is True


def test_evolution_failure_reports_error_and_resets_button(qapp):
    dashboard = AWCIDashboard()
    dashboard._on_real_physics_ready(_real_volume())
    dashboard.play_evolution_button.setEnabled(False)

    dashboard._on_evolution_failed("boom")

    assert dashboard.play_evolution_button.isEnabled() is True
    assert dashboard.play_evolution_button.text() == "▶ Play Evolution (4D)"
    assert "failed" in dashboard.real_physics_status.text().lower()


def test_revert_to_demo_stops_evolution_and_hides_play_button(qapp):
    dashboard = AWCIDashboard()
    dashboard._on_real_physics_ready(_real_volume())
    dashboard._on_evolution_ready(_real_evolution())
    assert dashboard._evolution_timer.isActive() is True

    dashboard._revert_to_demo()

    assert dashboard._evolution_timer.isActive() is False
    assert dashboard.play_evolution_button.isVisible() is False
    assert dashboard._evolution is None
    assert dashboard.time_readout.text() == f"{dashboard.time_slider.value():02d}Z"
