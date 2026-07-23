#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

echo "======================================="
echo " ACF Sprint 08 - Partie 3"
echo " Raster Renderer"
echo "======================================="

####################################################
# RASTER RENDERER
####################################################

cat > "$PROJECT/src/acf/maps/renderers/raster_renderer.py" << 'EOF'
"""
Raster Renderer
"""

import numpy as np

from acf.maps.styles.colormap_manager import ColorMapManager
from acf.maps.styles.colorbar_manager import ColorBarManager


class RasterRenderer:
    """
    Affiche une grille 2D sur la carte.
    """

    def __init__(self, canvas):

        self.canvas = canvas
        self.colormaps = ColorMapManager()
        self.colorbar = ColorBarManager(canvas)

    ##################################################

    def render(
        self,
        data,
        cmap="temperature",
        title="Raster",
        colorbar_label="",
    ):

        if not isinstance(data, np.ndarray):
            raise TypeError("data must be a numpy.ndarray")

        if data.ndim != 2:
            raise ValueError("RasterRenderer requires a 2D array")

        self.canvas.clear_canvas()

        cmap_obj = self.colormaps.get(cmap)

        image = self.canvas.axes.imshow(
            data,
            cmap=cmap_obj,
            origin="lower",
            interpolation="nearest",
        )

        self.canvas.axes.set_title(title)

        self.colorbar.draw(
            cmap=cmap_obj,
            vmin=float(np.nanmin(data)),
            vmax=float(np.nanmax(data)),
            label=colorbar_label,
        )

        return image
EOF

####################################################
# TESTS
####################################################

cat > "$PROJECT/tests/test_raster_renderer.py" << 'EOF'
import numpy as np

from acf.maps.canvas.map_canvas import MapCanvas
from acf.maps.renderers.raster_renderer import RasterRenderer


def test_renderer_creation(qtbot):

    canvas = MapCanvas()

    qtbot.addWidget(canvas)

    renderer = RasterRenderer(canvas)

    assert renderer is not None


def test_render(qtbot):

    canvas = MapCanvas()

    qtbot.addWidget(canvas)

    renderer = RasterRenderer(canvas)

    data = np.random.rand(30, 40)

    image = renderer.render(
        data,
        cmap="temperature",
        title="Demo",
        colorbar_label="Temperature"
    )

    assert image is not None
EOF

echo
echo "Raster Renderer installed successfully."
