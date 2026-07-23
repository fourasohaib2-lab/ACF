#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

echo "======================================="
echo " ACF Sprint 08 - Partie 5"
echo " Wind Renderer"
echo "======================================="

####################################################
# WIND RENDERER
####################################################

cat > "$PROJECT/src/acf/maps/renderers/wind_renderer.py" << 'EOF'
"""
Wind Renderer
"""

import numpy as np


class WindRenderer:

    def __init__(self, canvas):

        self.canvas = canvas

    ##################################################

    def render(
        self,
        u,
        v,
        stride=5,
        title="Wind Field"
    ):

        if not isinstance(u, np.ndarray):
            raise TypeError("u must be numpy.ndarray")

        if not isinstance(v, np.ndarray):
            raise TypeError("v must be numpy.ndarray")

        if u.shape != v.shape:
            raise ValueError("u and v must have the same shape")

        self.canvas.clear_canvas()

        ny, nx = u.shape

        x = np.arange(nx)
        y = np.arange(ny)

        X, Y = np.meshgrid(x, y)

        quiver = self.canvas.axes.quiver(
            X[::stride, ::stride],
            Y[::stride, ::stride],
            u[::stride, ::stride],
            v[::stride, ::stride]
        )

        self.canvas.axes.set_title(title)

        self.canvas.draw()

        return quiver
EOF

####################################################
# TESTS
####################################################

cat > "$PROJECT/tests/test_wind_renderer.py" << 'EOF'
import numpy as np

from acf.maps.canvas.map_canvas import MapCanvas
from acf.maps.renderers.wind_renderer import WindRenderer


def test_renderer_creation(qtbot):

    canvas = MapCanvas()

    qtbot.addWidget(canvas)

    renderer = WindRenderer(canvas)

    assert renderer is not None


def test_render(qtbot):

    canvas = MapCanvas()

    qtbot.addWidget(canvas)

    renderer = WindRenderer(canvas)

    u = np.ones((40, 40))
    v = np.ones((40, 40))

    result = renderer.render(
        u,
        v,
        stride=4
    )

    assert result is not None
EOF

echo
echo "Wind Renderer installed successfully."
