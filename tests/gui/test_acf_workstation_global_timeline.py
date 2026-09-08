"""
Tests for acf.gui.dashboard.acf_workstation_global_timeline.
ACFGlobalTimelineWidget - the real, on-demand multi-frame forecast-hour
scrubber (Phase 41, 2026-09-05).
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.awci.temporal_field import compute_real_complexity_evolution
from acf.awci.vertical_field import compute_real_complexity_volume
from acf.gui.dashboard.acf_workstation_global_timeline import N_FRAMES, STEPS_PER_FRAME, ACFGlobalTimelineWidget


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
        model="ALADIN", n_frames=N_FRAMES, steps_per_frame=STEPS_PER_FRAME,
        n_lat=10, n_lon=18, n_levels=5, perturbation_scale=2.0, seed=1,
    )
    kwargs.update(overrides)
    return compute_real_complexity_evolution(**kwargs)


def test_starts_with_no_real_evolution(qapp):
    widget = ACFGlobalTimelineWidget()
    assert widget.status() == {"has_evolution": False, "current_frame": None}
    assert widget.play_button.isEnabled() is False
    assert widget.frame_slider.isEnabled() is False


def test_run_without_a_volume_reports_an_honest_error(qapp):
    widget = ACFGlobalTimelineWidget()
    widget._start()
    assert "Run the Workstation" in widget.status_label.text()


def test_on_evolution_ready_populates_every_real_frame(qapp):
    widget = ACFGlobalTimelineWidget()
    widget.update_from_volume(_real_volume(), 0)

    widget._on_evolution_ready(_real_evolution())

    status = widget.status()
    assert status["has_evolution"] is True
    assert status["current_frame"] == 0
    assert widget.frame_slider.maximum() == N_FRAMES - 1
    assert set(widget.thumbnail_strip.status()["rendered"]) == set(widget.thumbnail_strip.status()["variables"])


def test_frame_labels_show_a_real_forecast_hour(qapp):
    widget = ACFGlobalTimelineWidget()
    widget.update_from_volume(_real_volume(), 0)
    evolution = _real_evolution()

    widget._on_evolution_ready(evolution)

    for i, name in enumerate(widget.thumbnail_strip.status()["variables"]):
        expected_hours = evolution["valid_time_seconds"][i] / 3600.0
        assert f"{expected_hours:.1f}h" in widget.thumbnail_strip._thumbnails[name].label_widget.text()


def test_scrubbing_the_slider_updates_the_real_status_readout(qapp):
    widget = ACFGlobalTimelineWidget()
    widget.update_from_volume(_real_volume(), 0)
    widget._on_evolution_ready(_real_evolution())

    widget.frame_slider.setValue(2)

    assert "Frame 3/" in widget.status_label.text()
    assert widget.status()["current_frame"] == 2


def test_clicking_a_thumbnail_moves_the_real_slider(qapp):
    widget = ACFGlobalTimelineWidget()
    widget.update_from_volume(_real_volume(), 0)
    widget._on_evolution_ready(_real_evolution())

    widget._on_thumbnail_clicked("Frame 4")

    assert widget.frame_slider.value() == 3


def test_advance_frame_wraps_around_at_the_real_last_frame(qapp):
    widget = ACFGlobalTimelineWidget()
    widget.update_from_volume(_real_volume(), 0)
    widget._on_evolution_ready(_real_evolution())
    widget.frame_slider.setValue(N_FRAMES - 1)

    widget._advance_frame()

    assert widget.frame_slider.value() == 0


def test_play_toggle_starts_and_stops_the_real_timer(qapp):
    widget = ACFGlobalTimelineWidget()
    widget.update_from_volume(_real_volume(), 0)
    widget._on_evolution_ready(_real_evolution())

    widget.play_button.setChecked(True)
    assert widget._timer.isActive() is True

    widget.play_button.setChecked(False)
    assert widget._timer.isActive() is False


def test_evolution_failure_reports_the_real_error_and_reenables_run(qapp):
    widget = ACFGlobalTimelineWidget()
    widget.run_button.setEnabled(False)

    widget._on_evolution_failed("boom")

    assert widget.run_button.isEnabled() is True
    assert "failed" in widget.status_label.text().lower()
