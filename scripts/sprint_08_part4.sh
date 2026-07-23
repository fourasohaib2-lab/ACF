#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

echo "======================================="
echo " ACF Sprint 08 - Partie 4"
echo " Contour Renderer"
echo "======================================="

####################################################
# CONTOUR RENDERER
####################################################

cat > "$PROJECT/src/acf/maps/renderers/contour_renderer.py" << 'EOF'
"""
Contour Renderer
"""

import numpy as np

from acf.maps.styles.colormap_manager import ColorMapManager
from acf.maps.styles.colorbar_manager import ColorBarManager


class ContourRenderer:

    def __init__(self, canvas):

        self.canvas = canvas

        self.colormaps = ColorMapManager()

        self.colorbar = ColorBarManager(canvas)

    ##################################################

    def render(
        self,
        data,
        cmap="temperature",
        levels=15,
        filled=True,
        title="Contour",
        colorbar_label=""
    ):

        if not isinstance(data, np.ndarray):
            raise TypeError("data must be numpy.ndarray")

        if data.ndim != 2:
            raise ValueError("ContourRenderer requires a 2D array")

        self.canvas.clear_canvas()

        cmap_obj = self.colormaps.get(cmap)

        if filled:

            contour = self.canvas.axes.contourf(
                data,
                levels=levels,
                cmap=cmap_obj
            )

        else:

            contour = self.canvas.axes.contour(
                data,
                levels=levels,
                colors="black"
            )

            self.canvas.axes.clabel(
                contour,
                inline=True,
                fontsize=8
            )

        self.canvas.axes.set_title(title)

        self.colorbar.draw(
            cmap=cmap_obj,
            vmin=float(np.nanmin(data)),
            vmax=float(np.nanmax(data)),
            label=colorbar_label
        )

        self.canvas.draw()

        return contour
EOF

####################################################
# TESTS
####################################################

cat > "$PROJECT/tests/test_contour_renderer.py" << 'EOF'
import numpy as np

from acf.maps.canvas.map_canvas import MapCanvas
from acf.maps.renderers.contour_renderer import ContourRenderer


def test_renderer_creation(qtbot):

    canvas = MapCanvas()

    qtbot.addWidget(canvas)

    renderer = ContourRenderer(canvas)

    assert renderer is not None


def test_render(qtbot):

    canvas = MapCanvas()

    qtbot.addWidget(canvas)

    renderer = ContourRenderer(canvas)

    data = np.random.rand(40,40)

    result = renderer.render(
        data,
        cmap="pressure",
        filled=True
    )

    assert result is not None
EOF

echo
echo
echo "Contour Renderer installed successfully."
