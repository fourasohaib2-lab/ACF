"""
Real visual regression test for ACFWorkstationWindow's Overview screen
(2026-09-13, master-prompt v4 Phase 38 gap audit).

Confirmed via `find` before this fix: no visual-regression test file
existed anywhere in tests/ (grep for "visual"/"regress"/"screenshot").

Honest scope of what this test can and cannot catch
-----------------------------------------------------
This renders the REAL `ACFWorkstationWindow` off-screen (Qt's own
"offscreen" QPA platform - the same technique this session used for a
real manual screenshot, not a mock), with a fully deterministic real
`CoupledEarthSolver` run (`ACFWorkstationWindow.__init__()` already
calls `refresh()`, and `refresh()`'s own `_VolumeWorker` uses a fixed
`seed=1` and the default ARPEGE model - genuinely reproducible, not
flaky from randomness).

It compares a DOWNSCALED thumbnail (80x50) average-color-per-cell
against a checked-in baseline (`tests/data/visual_baselines/
acf_workstation_overview.png`), not a raw pixel-for-pixel diff -
disclosed deliberately: font rasterization (anti-aliasing, hinting,
which system fonts are actually installed) genuinely differs across
machines/environments, so an exact pixel comparison would be a
constant source of false failures unrelated to any real UI regression.
The coarse thumbnail comparison is intentionally insensitive to sub-
pixel font rendering differences while still catching a REAL gross
layout regression - a panel disappearing, a color scheme changing, a
section collapsing to zero size, the window failing to render at all.

This is NOT a substitute for pixel-perfect fidelity to any external
reference mockup (already explicitly rejected as infeasible for a real
dynamic scientific app - see acf_workstation.py's own Phase 43
docstring entry) - it only catches this app regressing against ITS OWN
prior real render.

Updating the baseline (a deliberate step, when a real intentional UI
change is made): re-run this file's own `_render_workstation_png()`
manually and overwrite `tests/data/visual_baselines/
acf_workstation_overview.png`, then visually confirm the new PNG
before committing it - never regenerate it automatically to make a
failing test pass.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from PIL import Image
from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.acf_workstation_window import ACFWorkstationWindow

_BASELINE_PATH = Path(__file__).parent.parent / "data" / "visual_baselines" / "acf_workstation_overview.png"
_THUMBNAIL_SIZE = (80, 50)
_MAX_MEAN_ABS_DIFF = 12.0  # out of 255 per RGB channel, on the downscaled thumbnail - generous, tolerant of font AA drift


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _render_workstation_png(tmp_path: Path) -> Path:
    """Real off-screen render of the real window, with its own real,
    deterministic (seed=1) CoupledEarthSolver run already completed."""
    window = ACFWorkstationWindow()
    window.resize(1600, 1000)
    window.show()
    QApplication.processEvents()
    QThreadPool.globalInstance().waitForDone(30_000)
    QApplication.processEvents()
    QApplication.processEvents()

    out = tmp_path / "render.png"
    window.grab().save(str(out))
    window.close()
    return out


def _thumbnail_array(png_path: Path) -> np.ndarray:
    image = Image.open(png_path).convert("RGB").resize(_THUMBNAIL_SIZE)
    return np.asarray(image, dtype=np.float64)


def test_baseline_file_exists_and_is_a_real_non_trivial_image():
    assert _BASELINE_PATH.exists(), f"visual regression baseline missing: {_BASELINE_PATH}"
    baseline = Image.open(_BASELINE_PATH)
    assert baseline.size[0] > 100 and baseline.size[1] > 100


def test_overview_screen_matches_the_checked_in_baseline_within_tolerance(qapp, tmp_path):
    rendered_path = _render_workstation_png(tmp_path)

    rendered = _thumbnail_array(rendered_path)
    baseline = _thumbnail_array(_BASELINE_PATH)

    mean_abs_diff = float(np.mean(np.abs(rendered - baseline)))

    if mean_abs_diff > _MAX_MEAN_ABS_DIFF:
        debug_path = Path(__file__).parent.parent / "data" / "visual_baselines" / "_last_failure_render.png"
        Image.open(rendered_path).save(debug_path)
        pytest.fail(
            f"Overview screen drifted from the visual baseline: mean abs diff "
            f"{mean_abs_diff:.2f} > {_MAX_MEAN_ABS_DIFF} (thumbnail scale, 0-255 per channel). "
            f"Failing render saved to {debug_path} for inspection. If this is a deliberate "
            f"UI change, regenerate the baseline (see this test file's own module docstring) "
            f"after visually confirming the new render is correct."
        )
