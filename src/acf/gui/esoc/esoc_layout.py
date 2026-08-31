"""ESOC Layout Manager embedding Central Map, Sidebars, and Dock Panels (ACF-UI-011)."""

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDockWidget,
    QMainWindow,
    QTabWidget,
)

from acf.gui.esoc.esoc_sidebar import ESOCLeftSidebar, ESOCRightSidebar
from acf.gui.esoc.panel_manager import PanelManager
from acf.gui.esoc.view_manager import ViewManager


class ESOCLayout:
    """Manages the docking layout and panel positioning within ESOC QMainWindow."""

    def __init__(self, main_window: QMainWindow, panel_manager: PanelManager) -> None:
        self.main_window = main_window
        self.panel_manager = panel_manager

        # Central View Manager Map Canvas
        self.view_manager = ViewManager()
        self.main_window.setCentralWidget(self.view_manager)

        # Left Sidebar Dock
        self.left_sidebar = ESOCLeftSidebar()
        self.dock_left = QDockWidget("System Explorer", self.main_window)
        self.dock_left.setWidget(self.left_sidebar)
        self.main_window.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock_left)

        # Right Sidebar Dock
        self.right_sidebar = ESOCRightSidebar()
        self.dock_right = QDockWidget("Inspector & Diagnostics", self.main_window)
        self.dock_right.setWidget(self.right_sidebar)
        self.main_window.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_right)

        # Bottom Dock (Tabbed Operational Panels)
        self.bottom_tabs = QTabWidget()
        for name in self.panel_manager.list_panel_names():
            panel = self.panel_manager.get_panel(name)
            if panel:
                title = name.replace("_", " ").title()
                self.bottom_tabs.addTab(panel, title)

        self.dock_bottom = QDockWidget("Operational Command Panels", self.main_window)
        self.dock_bottom.setWidget(self.bottom_tabs)
        self.main_window.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.dock_bottom)

    def apply_workspace_profile(self, profile: dict[str, Any]) -> None:
        """Adjust panel visibility and focus according to workspace mode profile."""
        primary_panel = profile.get("primary_panel", "earth_monitoring")
        active_layers = profile.get("active_map_layers", [])

        # Update central map layers
        self.view_manager.set_layers(active_layers)

        # Select tab corresponding to primary panel
        for i in range(self.bottom_tabs.count()):
            tab_name = self.bottom_tabs.tabText(i).lower().replace(" ", "_")
            if primary_panel in tab_name:
                self.bottom_tabs.setCurrentIndex(i)
                break
