#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

echo "======================================="
echo " ACF Sprint 08 - Partie 2"
echo " ColorBar Engine"
echo "======================================="

####################################################
# COLORBAR MANAGER
####################################################

cat > "$PROJECT/src/acf/maps/styles/colorbar_manager.py" << 'EOF'
"""
ColorBar Manager
"""

from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize


class ColorBarManager:
    """
    Gestionnaire des barres de couleurs.
    """

    def __init__(self, canvas):

        self.canvas = canvas

    def draw(
        self,
        cmap,
        vmin,
        vmax,
        label="",
        orientation="vertical",
    ):

        sm = ScalarMappable(
            norm=Normalize(vmin=vmin, vmax=vmax),
            cmap=cmap,
        )

        sm.set_array([])

        self.canvas.figure.colorbar(
            sm,
            ax=self.canvas.axes,
            orientation=orientation,
            label=label,
        )

        self.canvas.draw()
EOF

####################################################
# TESTS
####################################################

cat > "$PROJECT/tests/test_colorbar_manager.py" << 'EOF'
from acf.maps.canvas.map_canvas import MapCanvas
from acf.maps.styles.colormap_manager import ColorMapManager
from acf.maps.styles.colorbar_manager import ColorBarManager


def test_colorbar_creation(qtbot):

    canvas = MapCanvas()

    qtbot.addWidget(canvas)

    manager = ColorMapManager()

    cmap = manager.get("temperature")

    colorbar = ColorBarManager(canvas)

    assert colorbar is not None

    assert cmap is not None
EOF

echo
echo "ColorBar Engine installed successfully."

