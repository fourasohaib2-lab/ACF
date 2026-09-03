"""
Tests for AWCICrossSection - specifically its real AWCI colorbar
(explicit user request "je veux garder le meme theme pour les deux en
suivant cette photo" - the reference mockup shows a real 0-100 AWCI
colorbar under this exact panel).
"""

from __future__ import annotations

from acf.gui.dashboard.awci_cross_section import AWCICrossSection

_POINT_A = (40.64, -73.78)
_POINT_B = (49.01, 2.55)


def test_colorbar_exists_after_first_draw(qtbot):
    panel = AWCICrossSection()
    qtbot.addWidget(panel)
    panel.update_data(_POINT_A, _POINT_B, cruise_hpa=300.0)
    assert panel._colorbar is not None
    assert len(panel.figure.axes) == 2  # main plot axes + colorbar axes


def test_colorbar_shows_the_real_0_to_100_awci_range(qtbot):
    panel = AWCICrossSection()
    qtbot.addWidget(panel)
    panel.update_data(_POINT_A, _POINT_B, cruise_hpa=300.0)
    ticks = list(panel._colorbar.get_ticks())
    assert ticks == [0, 20, 40, 60, 80, 100]


def test_repeated_redraws_do_not_stack_colorbars(qtbot):
    """Real regression guard: a colorbar owns its own Axes - redrawing
    without removing the previous one would silently accumulate a new
    colorbar axes on every update_data() call (e.g. every time_slider
    move in the real dashboard)."""
    panel = AWCICrossSection()
    qtbot.addWidget(panel)

    for _ in range(5):
        panel.update_data(_POINT_A, _POINT_B, cruise_hpa=300.0)

    assert len(panel.figure.axes) == 2


def test_repeated_redraws_do_not_raise_the_real_removal_bug():
    """Real regression guard for the exact bug found while building
    this: calling axis.clear() before colorbar.remove() raised
    "'NoneType' object has no attribute 'set_subplotspec'" on the
    second redraw - only reproducible by actually redrawing twice."""
    panel = AWCICrossSection()
    panel.update_data(_POINT_A, _POINT_B, cruise_hpa=300.0)
    panel.update_data(_POINT_A, _POINT_B, cruise_hpa=300.0)  # must not raise


def test_external_cross_section_also_gets_a_real_colorbar(qtbot):
    panel = AWCICrossSection()
    qtbot.addWidget(panel)
    distances = [0.0, 100.0, 200.0]
    levels_hpa = [1000.0, 700.0, 500.0]
    grid = [[10.0, 20.0, 30.0], [15.0, 25.0, 35.0], [5.0, 15.0, 25.0]]

    panel.set_external_cross_section(distances, levels_hpa, grid, "REAL PHYSICS")

    assert panel._colorbar is not None
    assert len(panel.figure.axes) == 2
