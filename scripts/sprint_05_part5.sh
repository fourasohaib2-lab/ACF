#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

echo "========================================"
echo " Sprint 05 - Part 5"
echo " Dashboard Integration"
echo "========================================"

cat > "$PROJECT/src/acf/dashboard/layout.py" << 'EOF'
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

        # Carte principale
        self.window.setCentralWidget(MapPanel())

        # Explorateur
        explorer = QDockWidget("Project Explorer")
        explorer.setObjectName("explorer")
        explorer.setWidget(ExplorerWidget())
        self.window.addDockWidget(Qt.LeftDockWidgetArea, explorer)

        # Graphiques
        charts = QDockWidget("Charts")
        charts.setObjectName("charts")
        charts.setWidget(ChartPanel())
        self.window.addDockWidget(Qt.RightDockWidgetArea, charts)

        # Propriétés
        properties = QDockWidget("Properties")
        properties.setObjectName("properties")
        properties.setWidget(PropertyPanel())
        self.window.addDockWidget(Qt.RightDockWidgetArea, properties)

        # Timeline
        timeline = QDockWidget("Timeline")
        timeline.setObjectName("timeline")
        timeline.setWidget(TimelinePanel())
        self.window.addDockWidget(Qt.BottomDockWidgetArea, timeline)

        # Console
        console = QDockWidget("Console")
        console.setObjectName("console")
        console.setWidget(ConsoleWidget())
        self.window.addDockWidget(Qt.BottomDockWidgetArea, console)

        # Statut
        status = QDockWidget("System Status")
        status.setObjectName("status")
        status.setWidget(StatusPanel())
        self.window.addDockWidget(Qt.BottomDockWidgetArea, status)

        # Organisation automatique
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
EOF

echo
echo "Dashboard Layout updated successfully."
