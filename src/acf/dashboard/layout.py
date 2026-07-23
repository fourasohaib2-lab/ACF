"""
Dashboard Layout
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDockWidget

from acf.dashboard.panels.map_panel import MapPanel
from acf.dashboard.panels.chart_panel import ChartPanel
from acf.dashboard.panels.timeline_panel import TimelinePanel
from acf.dashboard.panels.status_panel import StatusPanel

from acf.gui.widgets.console import ConsoleWidget
from acf.gui.widgets.explorer import ExplorerWidget
from acf.gui.widgets.property_panel import PropertyPanel


class DashboardLayout:

    def __init__(self, window):
        self.window = window

    def build(self):

        self.window.setCentralWidget(MapPanel())

        explorer = QDockWidget("Project Explorer")
        explorer.setWidget(ExplorerWidget())
        self.window.addDockWidget(Qt.LeftDockWidgetArea, explorer)

        charts = QDockWidget("Charts")
        charts.setWidget(ChartPanel())
        self.window.addDockWidget(Qt.RightDockWidgetArea, charts)

        properties = QDockWidget("Properties")
        properties.setWidget(PropertyPanel())
        self.window.addDockWidget(Qt.RightDockWidgetArea, properties)

        timeline = QDockWidget("Timeline")
        timeline.setWidget(TimelinePanel())
        self.window.addDockWidget(Qt.BottomDockWidgetArea, timeline)

        console = QDockWidget("Console")
        console.setWidget(ConsoleWidget())
        self.window.addDockWidget(Qt.BottomDockWidgetArea, console)

        status = QDockWidget("System Status")
        status.setWidget(StatusPanel())
        self.window.addDockWidget(Qt.BottomDockWidgetArea, status)

        self.window.tabifyDockWidget(properties, charts)
        self.window.tabifyDockWidget(console, timeline)

        explorer.show()
        charts.show()
        properties.show()
        timeline.show()
        console.show()
        status.show()

        return {
            "explorer": explorer,
            "charts": charts,
            "properties": properties,
            "timeline": timeline,
            "console": console,
            "status": status,
        }
