"""
Dashboard Layout
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDockWidget

from acf.dashboard.panels.chart_panel import ChartPanel
from acf.dashboard.panels.status_panel import StatusPanel
from acf.dashboard.panels.timeline_panel import TimelinePanel
from acf.gui.widgets.console import ConsoleWidget
from acf.gui.widgets.explorer import ExplorerWidget
from acf.gui.widgets.map_view import MapView
from acf.gui.widgets.property_panel import PropertyPanel


class DashboardLayout:
    def __init__(self, window):

        self.window = window

    def build(self):

        panels = {}

        # Carte principale

        map_view = MapView()

        self.window.setCentralWidget(map_view)

        panels["map"] = map_view

        # Explorer

        explorer = QDockWidget("Project Explorer")

        explorer_widget = ExplorerWidget()

        explorer.setWidget(explorer_widget)

        self.window.addDockWidget(Qt.LeftDockWidgetArea, explorer)

        panels["explorer"] = explorer_widget

        # Charts

        charts = QDockWidget("Scientific Charts")

        charts.setWidget(ChartPanel())

        self.window.addDockWidget(Qt.RightDockWidgetArea, charts)

        panels["charts"] = charts

        # Properties

        properties = QDockWidget("Properties")

        properties.setWidget(PropertyPanel())

        self.window.addDockWidget(Qt.RightDockWidgetArea, properties)

        panels["properties"] = properties

        # Timeline

        timeline = QDockWidget("Timeline")

        timeline.setWidget(TimelinePanel())

        self.window.addDockWidget(Qt.BottomDockWidgetArea, timeline)

        panels["timeline"] = timeline

        # Console

        console = QDockWidget("Console")

        console.setWidget(ConsoleWidget())

        self.window.addDockWidget(Qt.BottomDockWidgetArea, console)

        panels["console"] = console

        # Status

        status = QDockWidget("System Status")

        status.setWidget(StatusPanel())

        self.window.addDockWidget(Qt.BottomDockWidgetArea, status)

        panels["status"] = status

        return panels
