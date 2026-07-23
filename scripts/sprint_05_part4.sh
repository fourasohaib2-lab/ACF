#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

echo "======================================="
echo " Sprint 05 - Part 4"
echo " Dashboard Panels"
echo "======================================="

mkdir -p "$PROJECT/src/acf/dashboard/panels"

###########################################################
# MAP PANEL
###########################################################

cat > "$PROJECT/src/acf/dashboard/panels/map_panel.py" << 'EOF'
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout


class MapPanel(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        title = QLabel("🌍 Main Map")
        title.setStyleSheet("font-size:18px;font-weight:bold;")

        placeholder = QLabel(
            "Interactive map will appear here."
        )

        placeholder.setMinimumHeight(500)

        layout.addWidget(title)
        layout.addWidget(placeholder)
EOF

###########################################################
# CHART PANEL
###########################################################

cat > "$PROJECT/src/acf/dashboard/panels/chart_panel.py" << 'EOF'
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout


class ChartPanel(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        title = QLabel("📈 Scientific Charts")
        title.setStyleSheet("font-size:16px;font-weight:bold;")

        layout.addWidget(title)
        layout.addWidget(
            QLabel("Charts will appear here.")
        )
EOF

###########################################################
# TIMELINE PANEL
###########################################################

cat > "$PROJECT/src/acf/dashboard/panels/timeline_panel.py" << 'EOF'
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QSlider
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtCore import Qt


class TimelinePanel(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("⏱ Timeline"))

        slider = QSlider(Qt.Horizontal)

        slider.setMinimum(0)
        slider.setMaximum(100)

        layout.addWidget(slider)
EOF

###########################################################
# STATUS PANEL
###########################################################

cat > "$PROJECT/src/acf/dashboard/panels/status_panel.py" << 'EOF'
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QVBoxLayout


class StatusPanel(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("System Status"))

        layout.addWidget(
            QLabel("ACF Ready")
        )
EOF

echo
echo "Dashboard Panels successfully created."
