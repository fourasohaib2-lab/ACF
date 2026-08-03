"""Unified Earth System Operations Center (ESOC) Package (ACF-UI-011).

Integrates all ACF subsystems into a unified operational command center:
- Earth Monitoring & Physics
- Numerical Weather Prediction & Simulation Engine
- Earth Digital Twin & Planetary Dashboard
- Data Assimilation (4D-Var, EnKF, Hybrid)
- AI Forecast Intelligence & Emergency Assistant
- Hazard Operations (Cyclones, Floods, Storms, Wildfires)
- Climate Scenarios (CMIP6 / SSP) & Projections
- Forecast Verification Metrics
- HPC Computing & GPU Acceleration Layer
"""

from acf.gui.esoc.module_registry import ModuleRegistry
from acf.gui.esoc.command_dispatcher import CommandDispatcher
from acf.gui.esoc.session_manager import SessionManager
from acf.gui.esoc.esoc_workspace import WorkspaceMode, WorkspaceManager
from acf.gui.esoc.panel_manager import PanelManager
from acf.gui.esoc.view_manager import ViewManager
from acf.gui.esoc.esoc_sidebar import ESOCLeftSidebar, ESOCRightSidebar
from acf.gui.esoc.esoc_toolbar import ESOCToolbar
from acf.gui.esoc.esoc_statusbar import ESOCStatusBar
from acf.gui.esoc.esoc_layout import ESOCLayout
from acf.gui.esoc.esoc_controller import ESOCController
from acf.gui.esoc.esoc_window import ESOCWindow

__all__ = [
    "ModuleRegistry",
    "CommandDispatcher",
    "SessionManager",
    "WorkspaceMode",
    "WorkspaceManager",
    "PanelManager",
    "ViewManager",
    "ESOCLeftSidebar",
    "ESOCRightSidebar",
    "ESOCToolbar",
    "ESOCStatusBar",
    "ESOCLayout",
    "ESOCController",
    "ESOCWindow",
]
