"""
GUI-level tests for
acf.gui.dashboard.acf_workstation_temporal.ACFTemporalLabPanel - the
real on-demand multi-frame evolution worker/frame-slider wiring.
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.awci.vertical_field import compute_real_complexity_volume
from acf.gui.dashboard.acf_workstation_temporal import ACFTemporalLabPanel


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _real_small_volume(**overrides):
    kwargs = dict(model="ALADIN", n_lat=4, n_lon=4, n_levels=4, steps=2, perturbation_scale=2.0, seed=1)
    kwargs.update(overrides)
    return compute_real_complexity_volume(**kwargs)


def test_starts_with_no_evolution_and_disabled_frame_slider(qapp):
    panel = ACFTemporalLabPanel()
    assert panel._evolution is None
    assert panel.frame_slider.isEnabled() is False
    assert "Not yet computed" in panel.status_label.text()


def test_run_button_without_a_volume_reports_an_honest_error(qapp):
    panel = ACFTemporalLabPanel()

    panel._start_evolution()

    assert "Run the Workstation" in panel.status_label.text()


def test_clicking_run_genuinely_runs_off_thread_and_populates_the_frame_slider(qtbot):
    """Drives the actual QThreadPool.globalInstance().start() + Qt
    event loop path, not a direct call - same discipline as this
    codebase's other real-worker tests."""
    panel = ACFTemporalLabPanel()
    qtbot.addWidget(panel)
    panel.update_from_volume(_real_small_volume(), level_index=0)

    panel.run_button.click()

    qtbot.waitUntil(lambda: panel._evolution is not None, timeout=60000)
    assert panel.frame_slider.isEnabled() is True
    assert panel.frame_slider.maximum() == panel._evolution["n_frames"] - 1
    assert "✅" in panel.status_label.text()
    assert panel.map_panel.status()["has_contour"] is True
    assert "t+" in panel.frame_label.text()


def test_moving_the_frame_slider_redraws_without_a_new_solver_run(qtbot, monkeypatch):
    """Real regression guard: scrubbing frames must re-slice the
    already-computed evolution, never trigger a second real solver
    run."""
    panel = ACFTemporalLabPanel()
    qtbot.addWidget(panel)
    panel.update_from_volume(_real_small_volume(), level_index=0)
    panel.run_button.click()
    qtbot.waitUntil(lambda: panel._evolution is not None, timeout=60000)

    def _fail_if_called(*_args, **_kwargs):
        raise AssertionError("a new solver run must not happen on a frame change")

    monkeypatch.setattr("acf.gui.dashboard.acf_workstation_temporal.compute_real_complexity_evolution", _fail_if_called)

    panel.frame_slider.setValue(panel.frame_slider.maximum())

    assert panel.frame_label.text().startswith(str(panel.frame_slider.maximum() + 1))


def test_evolution_result_is_not_reset_by_a_level_change(qtbot):
    """Same real "stays whatever it was" convention already documented
    on Complexity Explorer's own temporal/consensus dimensions and
    Thermodynamics Lab's own CAPE/CIN."""
    panel = ACFTemporalLabPanel()
    qtbot.addWidget(panel)
    volume = _real_small_volume()
    panel.update_from_volume(volume, level_index=0)
    panel.run_button.click()
    qtbot.waitUntil(lambda: panel._evolution is not None, timeout=60000)
    evolution_before = panel._evolution

    panel.update_from_volume(volume, level_index=volume["n_levels"] - 1)

    assert panel._evolution is evolution_before
