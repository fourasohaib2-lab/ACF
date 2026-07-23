#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

echo "======================================="
echo " ACF Sprint 07 - Partie 6"
echo " Cartopy Renderer"
echo "======================================="

####################################################
# CARTOPY RENDERER
####################################################

cat > "$PROJECT/src/acf/maps/renderers/cartopy_renderer.py" << 'EOF'
"""
Cartopy Renderer
"""

import cartopy.crs as ccrs
import cartopy.feature as cfeature


class CartopyRenderer:

    def __init__(self, canvas):

        self.canvas = canvas

    def draw_world(self):

        self.canvas.figure.clear()

        ax = self.canvas.figure.add_subplot(
            111,
            projection=ccrs.PlateCarree()
        )

        ax.set_global()

        ax.add_feature(cfeature.LAND)
        ax.add_feature(cfeature.OCEAN)
        ax.add_feature(cfeature.COASTLINE)
        ax.add_feature(cfeature.BORDERS)

        ax.gridlines(draw_labels=True)

        ax.set_title("Atmospheric Complexity Framework")

        self.canvas.axes = ax

        self.canvas.draw()
EOF

####################################################
# MAP CANVAS
####################################################

cat > "$PROJECT/src/acf/maps/canvas/map_canvas.py" << 'EOF'
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from acf.maps.renderers.cartopy_renderer import CartopyRenderer


class MapCanvas(FigureCanvasQTAgg):

    def __init__(self):

        self.figure = Figure(figsize=(12,8))

        super().__init__(self.figure)

        self.axes = None

        self.renderer = CartopyRenderer(self)

    def draw_world(self):

        self.renderer.draw_world()
EOF

####################################################
# TESTS
####################################################

cat > "$PROJECT/tests/test_cartopy_renderer.py" << 'EOF'
from acf.maps.canvas.map_canvas import MapCanvas


def test_renderer_creation(qtbot):

    canvas = MapCanvas()

    qtbot.addWidget(canvas)

    assert canvas.renderer is not None
EOF

echo
echo "Cartopy Renderer installed successfully."
