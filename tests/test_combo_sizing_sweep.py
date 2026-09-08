"""
Real responsive-sizing regression test for the 3 remaining QComboBox
instances found by grepping this codebase for combo items longer than
28 characters (same defect class as acf.gui.esoc.view_manager's own
combos - see acf.gui.widgets.combo_sizing's module docstring):

- SimulationPanel.combo_physics ("Non-Hydrostatic Finite Volume",
  "Spherical Spectral Wave Solver")
- DigitalTwinPanel.combo ("CMIP6 SSP5-8.5 (Fossil-Fueled)" and 11 other
  scenario names)
- ESOCRightSidebar.combo_chart ("Taylor Diagram (Forecast
  Verification)")

Each of these sits inside a container this session already protected
against propagating an inflated child minimum up to the whole window
(ESOCLayout.bottom_tabs's QScrollArea wrap for the first two,
CurrentPageTabWidget for the third) - so this is a smaller-magnitude,
contained fix (that specific tab's own minimum width, not the whole
app), applied for the same consistency reason as the rest of this
audit: the same real bug, wherever it turns up.
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication, QComboBox

from acf.gui.esoc.esoc_sidebar import ESOCRightSidebar
from acf.gui.esoc.module_registry import ModuleRegistry
from acf.gui.esoc.panel_manager import DigitalTwinPanel, PanelManager, SimulationPanel


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def panel_manager(qapp):
    from acf.gui.esoc.command_dispatcher import CommandDispatcher

    return PanelManager(ModuleRegistry(), CommandDispatcher())


def _uses_min_contents_length_policy(combo: QComboBox) -> bool:
    return combo.sizeAdjustPolicy() == QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon


def test_simulation_panel_physics_combo_does_not_adjust_to_its_longest_item(panel_manager, qapp):
    panel = panel_manager.get_panel("simulation")
    assert isinstance(panel, SimulationPanel)
    assert _uses_min_contents_length_policy(panel.combo_physics)
    # Real content untouched.
    assert panel.combo_physics.findText("Spherical Spectral Wave Solver") != -1


def test_digital_twin_panel_combo_does_not_adjust_to_its_longest_item(panel_manager, qapp):
    panel = panel_manager.get_panel("digital_twin")
    assert isinstance(panel, DigitalTwinPanel)
    assert _uses_min_contents_length_policy(panel.combo)
    assert panel.combo.findText("CMIP6 SSP5-8.5 (Fossil-Fueled)") != -1


def test_right_sidebar_chart_combo_does_not_adjust_to_its_longest_item(qapp):
    sidebar = ESOCRightSidebar()
    assert _uses_min_contents_length_policy(sidebar.combo_chart)
    assert sidebar.combo_chart.findText("Taylor Diagram (Forecast Verification)") != -1
