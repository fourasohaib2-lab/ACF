"""ESOC Layout Manager embedding Central Map, Sidebars, and Dock Panels (ACF-UI-011).

NOTE (correction, 2026-09-04): ESOCLeftSidebar's `on_select_callback`
had a real signature and a real `tree.itemClicked` connection, but
`ESOCLayout` (its only real caller) never supplied one - every one of
the System Explorer tree's ~150 real leaves was a genuine no-op click,
the same class of "dead button" this project has repeatedly found and
fixed elsewhere in ESOC. Fixed here by wiring a real
`_on_sidebar_item_selected()` that switches `self.bottom_tabs` to the
matching real `panel_manager.py` panel - but ONLY for labels verified
below to correspond to one. Many tree labels (originally an entire
"Catalog"/"Products"/"Reports"/"Output"/"Plugins" category's worth,
plus several individual leaves under categories that do have a panel)
had no real operational panel behind them at all - clicking those
stayed an honest no-op rather than a guessed/wrong navigation. See the
two mapping tables' own docstring for exactly which labels were
verified real and which were deliberately left unmapped.

UPDATE (2026-09-04, same day): "Catalog" and "Plugins" are real and
wired now - see `CatalogPanel`/`PluginsPanel`'s own docstrings in
`panel_manager.py`. The remaining 3 categories named above
(Products/Reports/Output) plus Geoengineering/Machine Learning (not
originally named here) remain real, disclosed, in-progress work - each
will be updated here as it gets a real panel, not silently left stale.
"""

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDockWidget,
    QMainWindow,
    QTabWidget,
)

from acf.gui.esoc.esoc_sidebar import ESOCLeftSidebar, ESOCRightSidebar
from acf.gui.esoc.module_registry import ModuleRegistry
from acf.gui.esoc.panel_manager import PanelManager
from acf.gui.esoc.view_manager import ViewManager

#: Real System Explorer tree LEAF label -> real panel_manager.py panel
#: key, verified one at a time (each label's own real matching panel
#: exists and is thematically unambiguous - e.g. the tree's "Ocean"
#: leaf and panel_manager's own "ocean" -> OceanPanel). Checked against
#: EVERY leaf in ESOCLeftSidebar's own self.categories, not just these
#: - the rest genuinely have no real panel to point to yet.
_LEAF_LABEL_TO_PANEL_NAME: dict[str, str] = {
    "Ocean": "ocean",
    "Hydrology": "hydrology",
    "Cryosphere": "cryosphere",
    "Air Quality": "air_quality",
    "Geology": "geology",
    "Carbon Cycle": "carbon",
    "Job Explorer": "job_explorer",
    "Storage & Scratch": "storage_monitor",
    "Remote Terminal": "hpc_terminal",
    "CUDA GPU Monitor": "gpu_monitor",
    "Benchmarks": "benchmark_panel",
    "HPC Profiles": "hpc_dashboard",
    "System Config": "system_console",
}

#: Real System Explorer top-level CATEGORY label -> real
#: panel_manager.py panel key, for domains with exactly one real panel
#: covering every leaf under that category (e.g. every "Simulation"
#: leaf - "Coupled Earth Solver"/"Finite Volume"/"Spectral Solver"/
#: "AMR" - opens the one real SimulationPanel; there is no real
#: per-solver-type panel to distinguish between them). Applied to a
#: leaf only when that leaf itself has no more specific entry in
#: `_LEAF_LABEL_TO_PANEL_NAME` above, and also matches a click on the
#: category header item itself. "Earth System" and "HPC" are
#: deliberately absent here - each has SEVERAL distinct real panels
#: among its own leaves (see the table above), not one.
_CATEGORY_LABEL_TO_PANEL_NAME: dict[str, str] = {
    "Forecast": "forecast",
    "Assimilation": "data_assimilation",
    "Simulation": "simulation",
    "Digital Twin": "digital_twin",
    "Climate": "climate",
    "Planetary Limits": "planetary_dashboard",
    "Earth Physics": "earth_physics",
    "Monitoring": "earth_monitoring",
    "Verification": "verification",
    "Catalog": "catalog",
    "Plugins": "plugins",
}


class ESOCLayout:
    """Manages the docking layout and panel positioning within ESOC QMainWindow."""

    def __init__(
        self,
        main_window: QMainWindow,
        panel_manager: PanelManager,
        registry: ModuleRegistry | None = None,
    ) -> None:
        self.main_window = main_window
        self.panel_manager = panel_manager

        # Central View Manager Map Canvas
        self.view_manager = ViewManager()
        self.main_window.setCentralWidget(self.view_manager)

        # Left Sidebar Dock - registry (added 2026-09-04) gives its
        # own real "🔍 Universal Search" a real ModuleRegistry.
        # global_search() backend - see ESOCLeftSidebar's own NOTE.
        # on_select_callback (added same day - see this module's own
        # NOTE) makes a tree click with a real matching panel actually
        # switch to it.
        self.left_sidebar = ESOCLeftSidebar(
            registry=registry, on_select_callback=self._on_sidebar_item_selected
        )
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

    def _on_sidebar_item_selected(self, label: str, category: str | None) -> None:
        """Real routing from a System Explorer tree click to the real
        operational panel it corresponds to (see this module's own
        NOTE for the full disclosure of why most of this tree's ~150
        leaves stay a real, honest no-op here). A leaf's own specific
        mapping wins over its category's; a category header clicked
        directly (category is None then, since it has no parent) is
        looked up as a leaf too, so e.g. clicking "Simulation" itself
        also opens the SimulationPanel."""
        panel_name = _LEAF_LABEL_TO_PANEL_NAME.get(label) or _CATEGORY_LABEL_TO_PANEL_NAME.get(label)
        if panel_name is None and category is not None:
            panel_name = _CATEGORY_LABEL_TO_PANEL_NAME.get(category)
        if panel_name is None:
            return  # no real panel for this label - an honest no-op, not a guess

        panel = self.panel_manager.get_panel(panel_name)
        if panel is None:
            return

        index = self.bottom_tabs.indexOf(panel)
        if index == -1:
            return
        self.bottom_tabs.setCurrentIndex(index)
        self.dock_bottom.setVisible(True)
        self.dock_bottom.raise_()

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
