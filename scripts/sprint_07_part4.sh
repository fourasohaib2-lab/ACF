#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

echo "======================================="
echo " ACF Sprint 07 - Partie 4"
echo " Map Canvas"
echo "======================================="

####################################################
# MAP CANVAS
####################################################

cat > "$PROJECT/src/acf/maps/canvas/map_canvas.py" << 'EOF'
"""
Map Canvas
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QWidget


class MapCanvas(QWidget):
    """
    Zone centrale de dessin des cartes.
    """

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setMinimumSize(800, 600)

        self.zoom = 1.0
        self.center_x = 0
        self.center_y = 0

        self.setMouseTracking(True)

    ##################################################

    def zoom_in(self):

        self.zoom *= 1.2
        self.update()

    ##################################################

    def zoom_out(self):

        self.zoom /= 1.2
        self.update()

    ##################################################

    def reset_view(self):

        self.zoom = 1.0
        self.center_x = 0
        self.center_y = 0
        self.update()

    ##################################################

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.fillRect(self.rect(), QColor(25, 30, 45))

        painter.setPen(Qt.white)

        painter.drawText(
            self.rect(),
            Qt.AlignCenter,
            f"Atmospheric Complexity Framework\nMap Canvas\nZoom : {self.zoom:.2f}x"
        )
EOF

####################################################
# TESTS
####################################################

cat > "$PROJECT/tests/test_map_canvas.py" << 'EOF'
from acf.maps.canvas.map_canvas import MapCanvas


def test_canvas_creation(qtbot):

    canvas = MapCanvas()

    qtbot.addWidget(canvas)

    assert canvas.zoom == 1.0


def test_zoom(qtbot):

    canvas = MapCanvas()

    qtbot.addWidget(canvas)

    canvas.zoom_in()

    assert canvas.zoom > 1

    canvas.reset_view()

    assert canvas.zoom == 1.0
EOF

echo
echo "Map Canvas installed successfully."
