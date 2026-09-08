"""
Tests for AWCIMapPanel's `show_demo_fallback` constructor parameter
(added 2026-09-04).

Regression guard for a real bug found while screenshot-verifying the
ACF Scientific Workstation (`acf.gui.dashboard.acf_workstation*`,
explicit user master spec: "ACF CORE ONLY - NO AWCI"): the
Workstation's own "TEMPORAL COMPLEXITY" map panel was rendering a
colorful, real-looking contour map even though "Run Temporal Analysis"
had never been clicked and its own status label still read "Not yet
computed". Root cause: `AWCIMapPanel.update_data()` unconditionally
fell back to AWCI's own synthetic demo pattern (`awci_grid()`)
whenever `set_external_field()` had never been called - correct and
disclosed behaviour for AWCI's own dashboard, but a real violation of
the Workstation's "no AWCI content anywhere" principle for panels that
have not yet been given real data.
"""

from __future__ import annotations

import numpy as np

from acf.gui.dashboard.awci_map_panel import AWCIMapPanel


def test_show_demo_fallback_defaults_to_true_zero_behaviour_change_for_awci(qtbot):
    """Every existing AWCI caller passes no show_demo_fallback at all -
    confirms the new parameter's default preserves their real,
    existing behaviour exactly (the synthetic demo pattern still
    renders when no external field has been set)."""
    panel = AWCIMapPanel("AWCI GLOBAL MAP")
    qtbot.addWidget(panel)
    assert panel._show_demo_fallback is True
    assert panel.status()["has_contour"] is True


def test_show_demo_fallback_false_renders_an_honest_blank_map_not_awci_demo_content(qtbot):
    panel = AWCIMapPanel("WORKSTATION PANEL", show_demo_fallback=False)
    qtbot.addWidget(panel)

    captured: dict[str, np.ndarray] = {}
    original_contourf = panel.axis.contourf

    def _capture_contourf(lons, lats, grid, **kwargs):
        captured["grid"] = np.asarray(grid)
        return original_contourf(lons, lats, grid, **kwargs)

    panel.axis.contourf = _capture_contourf
    panel.update_data()

    assert "grid" in captured
    # A genuinely blank map (all-NaN), never AWCI's fabricated pattern.
    assert np.isnan(captured["grid"]).all()


def test_show_demo_fallback_false_still_shows_a_real_external_field_once_set(qtbot):
    """show_demo_fallback only suppresses the DEMO fallback - a real
    field supplied via set_external_field() must still render exactly
    as before."""
    panel = AWCIMapPanel("WORKSTATION PANEL", show_demo_fallback=False)
    qtbot.addWidget(panel)
    lons = [0.0, 10.0]
    lats = [0.0, 10.0]
    grid = [[1.0, 2.0], [3.0, 4.0]]

    captured: dict[str, np.ndarray] = {}
    original_contourf = panel.axis.contourf

    def _capture_contourf(lons_, lats_, grid_, **kwargs):
        captured["grid"] = np.asarray(grid_)
        return original_contourf(lons_, lats_, grid_, **kwargs)

    panel.axis.contourf = _capture_contourf
    panel.set_external_field(lons, lats, grid, "Real field")

    assert "grid" in captured
    assert not np.isnan(captured["grid"]).any()
    assert captured["grid"].tolist() == grid


def test_show_demo_fallback_false_still_produces_a_real_status_with_a_contour(qtbot):
    """The blank NaN map is still a real matplotlib contour object
    (status()["has_contour"] stays True) - only its content is honest,
    not the panel's own rendering machinery."""
    panel = AWCIMapPanel("WORKSTATION PANEL", show_demo_fallback=False)
    qtbot.addWidget(panel)
    assert panel.status()["has_contour"] is True
