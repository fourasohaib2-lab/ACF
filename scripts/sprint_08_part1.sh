#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

echo "======================================="
echo " ACF Sprint 08 - Partie 1"
echo " ColorMap Engine"
echo "======================================="

mkdir -p "$PROJECT/src/acf/maps/styles"

####################################################
# COLORMAP MANAGER
####################################################

cat > "$PROJECT/src/acf/maps/styles/colormap_manager.py" << 'EOF'
"""
ColorMap Manager
"""

import matplotlib.pyplot as plt


class ColorMapManager:

    def __init__(self):

        self._maps = {
            "temperature": "coolwarm",
            "pressure": "viridis",
            "humidity": "Blues",
            "precipitation": "turbo",
            "wind": "plasma",
            "terrain": "terrain",
            "clouds": "Greys",
        }

    def available(self):

        return sorted(self._maps.keys())

    def get(self, name):

        if name not in self._maps:
            raise ValueError(
                f"Unknown colormap: {name}"
            )

        return plt.get_cmap(self._maps[name])

    def register(self, name, cmap):

        self._maps[name] = cmap
EOF

####################################################
# TESTS
####################################################

cat > "$PROJECT/tests/test_colormap_manager.py" << 'EOF'
from acf.maps.styles.colormap_manager import ColorMapManager


def test_default_maps():

    manager = ColorMapManager()

    assert "temperature" in manager.available()
    assert "pressure" in manager.available()


def test_get_map():

    manager = ColorMapManager()

    cmap = manager.get("temperature")

    assert cmap is not None


def test_register():

    manager = ColorMapManager()

    manager.register("ozone", "viridis")

    assert "ozone" in manager.available()
EOF

echo
echo "ColorMap Manager successfully installed."
