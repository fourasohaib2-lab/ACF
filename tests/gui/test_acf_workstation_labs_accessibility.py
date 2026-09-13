"""
Real accessibility regression tests for the "value-only" selectors
(QComboBox/QSlider) of the 13 ACF Workstation Lab panels
(`acf.gui.dashboard.acf_workstation_*`) reachable via ACFWorkstation's
own nav/"More Labs" menu (2026-09-13 follow-up to the shell-level
accessibility fix).

Scope, disclosed honestly: each of these selectors already has a real,
visible adjacent QLabel (e.g. "Variable:") - Qt does not automatically
associate that QLabel with the QComboBox/QSlider next to it for a
screen reader (that requires either QLabel.setBuddy() - not used
anywhere in this codebase - or an explicit accessibleName on the
control itself), so without one a screen reader announces only the
selector's current value, with no context for what it selects. Same
gap class, same fix (setAccessibleName reusing the real adjacent
label's own text), as the one already closed on ACFWorkstation's own
shell (model_selector/domain_selector) and AWCIMapPanel/MapCanvas
(icon-only buttons).

One consolidated test file rather than 13 near-identical additions to
13 separate existing test files - the assertion is the same one-liner
per panel, and this keeps the real duplication visible in one place
instead of scattered.
"""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from acf.gui.dashboard.acf_workstation_3d import ACF3DAtmospherePanel
from acf.gui.dashboard.acf_workstation_confidence import ACFConfidenceLabPanel
from acf.gui.dashboard.acf_workstation_convection import ACFConvectionLabPanel
from acf.gui.dashboard.acf_workstation_dynamics import ACFDynamicsLabPanel
from acf.gui.dashboard.acf_workstation_global_timeline import ACFGlobalTimelineWidget
from acf.gui.dashboard.acf_workstation_interactions import ACFInteractionEnginePanel
from acf.gui.dashboard.acf_workstation_microphysics import ACFMicrophysicsLabPanel
from acf.gui.dashboard.acf_workstation_multimodel import ACFMultiModelLabPanel
from acf.gui.dashboard.acf_workstation_overview import ACFOverviewPanel
from acf.gui.dashboard.acf_workstation_quality import ACFDataQualityLabPanel
from acf.gui.dashboard.acf_workstation_temporal import ACFTemporalLabPanel
from acf.gui.dashboard.acf_workstation_terrain import ACFTerrainLabPanel
from acf.gui.dashboard.acf_workstation_thermodynamics import ACFThermodynamicsLabPanel


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.mark.parametrize(
    ("panel_cls", "attr", "expected_name"),
    [
        (ACF3DAtmospherePanel, "variable_selector", "Variable selector"),
        (ACFConfidenceLabPanel, "variable_selector", "Variable selector"),
        (ACFConvectionLabPanel, "variable_selector", "Variable selector"),
        (ACFDynamicsLabPanel, "variable_selector", "Variable selector"),
        (ACFGlobalTimelineWidget, "speed_selector", "Speed selector"),
        (ACFGlobalTimelineWidget, "frame_slider", "Frame selector"),
        (ACFInteractionEnginePanel, "variable_a_selector", "Variable A selector"),
        (ACFInteractionEnginePanel, "variable_b_selector", "Variable B selector"),
        (ACFMicrophysicsLabPanel, "variable_selector", "Variable selector"),
        (ACFMultiModelLabPanel, "model_a_selector", "Model A selector"),
        (ACFMultiModelLabPanel, "model_b_selector", "Model B selector"),
        (ACFMultiModelLabPanel, "display_selector", "Display field selector"),
        (ACFOverviewPanel, "variable_selector", "Variable selector"),
        (ACFDataQualityLabPanel, "variable_selector", "Variable selector"),
        (ACFTemporalLabPanel, "variable_selector", "Variable selector"),
        (ACFTemporalLabPanel, "frame_slider", "Frame selector"),
        (ACFTerrainLabPanel, "variable_selector", "Variable selector"),
        (ACFThermodynamicsLabPanel, "variable_selector", "Variable selector"),
        (ACFThermodynamicsLabPanel, "cape_variable_selector", "CAPE/CIN variable selector"),
    ],
)
def test_lab_panel_selector_has_a_real_accessible_name(qapp, panel_cls, attr, expected_name):
    panel = panel_cls()

    assert getattr(panel, attr).accessibleName() == expected_name
