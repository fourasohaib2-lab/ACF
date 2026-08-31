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

from acf.gui.esoc.command_dispatcher import CommandDispatcher
from acf.gui.esoc.esoc_controller import ESOCController
from acf.gui.esoc.esoc_layout import ESOCLayout
from acf.gui.esoc.esoc_sidebar import ESOCLeftSidebar, ESOCRightSidebar
from acf.gui.esoc.esoc_statusbar import ESOCStatusBar
from acf.gui.esoc.esoc_toolbar import ESOCToolbar
from acf.gui.esoc.esoc_window import ESOCWindow
from acf.gui.esoc.esoc_workspace import WorkspaceManager, WorkspaceMode
from acf.gui.esoc.hpc_dashboard_panel import HPCDashboardPanel
from acf.gui.esoc.hpc_execution_panel import HPCExecutionPanel
from acf.gui.esoc.module_registry import ModuleRegistry
from acf.gui.esoc.nwp_forecast_center_panel import NWPForecastCenterPanel
from acf.gui.esoc.panel_manager import PanelManager
from acf.gui.esoc.session_manager import SessionManager
from acf.gui.esoc.view_manager import ViewManager

__all__ = [
    "CommandDispatcher",
    "ESOCController",
    "ESOCLayout",
    "ESOCLeftSidebar",
    "ESOCRightSidebar",
    "ESOCStatusBar",
    "ESOCToolbar",
    "ESOCWindow",
    "HPCDashboardPanel",
    "HPCExecutionPanel",
    "ModuleRegistry",
    "NWPForecastCenterPanel",
    "PanelManager",
    "SessionManager",
    "ViewManager",
    "WorkspaceManager",
    "WorkspaceMode",
]
