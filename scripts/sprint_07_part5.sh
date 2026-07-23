#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

echo "======================================="
echo " ACF Sprint 07 - Partie 5"
echo " Matplotlib Map Canvas"
echo "======================================="

cat > "$PROJECT/src/acf/maps/canvas/map_canvas.py" << 'EOF'
"""
Map Canvas
"""

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class MapCanvas(FigureCanvasQTAgg):
    """
    Canvas Matplotlib intégré à Qt.
    """

    def __init__(self):

        self.figure = Figure(figsize=(10, 8))

        super().__init__(self.figure)

        self.axes = self.figure.add_subplot(111)

        self.initialize()

    ##################################################

    def initialize(self):

        self.axes.set_title("Atmospheric Complexity Framework")

        self.axes.set_xlabel("Longitude")

        self.axes.set_ylabel("Latitude")

        self.axes.grid(True)

        self.draw()

    ##################################################

    def clear_canvas(self):

        self.axes.clear()

        self.initialize()

    ##################################################

    def plot_demo(self):

        x = [0, 1, 2, 3, 4]

        y = [0, 1, 4, 9, 16]

        self.axes.clear()

        self.axes.plot(x, y)

        self.axes.set_title("Demo Plot")

        self.draw()
EOF

cat > "$PROJECT/tests/test_map_canvas.py" << 'EOF'
from acf.maps.canvas.map_canvas import MapCanvas


def test_canvas_creation(qtbot):

    canvas = MapCanvas()

    qtbot.addWidget(canvas)

    assert canvas.axes is not None


def test_plot(qtbot):

    canvas = MapCanvas()

    qtbot.addWidget(canvas)

    canvas.plot_demo()

    assert len(canvas.axes.lines) == 1
EOF

echo
echo "Matplotlib Canvas successfully installed."
