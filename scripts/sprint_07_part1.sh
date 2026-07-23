#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

echo "======================================="
echo " ACF Sprint 07 - Part 1"
echo " Cartography Engine"
echo "======================================="

#######################################################
# Création de l'arborescence
#######################################################

mkdir -p "$PROJECT/src/acf/maps"

mkdir -p "$PROJECT/src/acf/maps/renderers"
mkdir -p "$PROJECT/src/acf/maps/layers"
mkdir -p "$PROJECT/src/acf/maps/projections"
mkdir -p "$PROJECT/src/acf/maps/canvas"
mkdir -p "$PROJECT/src/acf/maps/styles"

touch "$PROJECT/src/acf/maps/__init__.py"

touch "$PROJECT/src/acf/maps/map_engine.py"
touch "$PROJECT/src/acf/maps/map_manager.py"

touch "$PROJECT/src/acf/maps/renderers/__init__.py"
touch "$PROJECT/src/acf/maps/renderers/cartopy_renderer.py"

touch "$PROJECT/src/acf/maps/layers/__init__.py"
touch "$PROJECT/src/acf/maps/layers/base_layer.py"

touch "$PROJECT/src/acf/maps/projections/__init__.py"
touch "$PROJECT/src/acf/maps/projections/projection_manager.py"

touch "$PROJECT/src/acf/maps/canvas/__init__.py"
touch "$PROJECT/src/acf/maps/canvas/map_canvas.py"

touch "$PROJECT/src/acf/maps/styles/__init__.py"
touch "$PROJECT/src/acf/maps/styles/color_table.py"

#######################################################
# Map Engine
#######################################################

cat > "$PROJECT/src/acf/maps/map_engine.py" << 'EOF'
"""
ACF Map Engine
"""

class MapEngine:

    def __init__(self):

        self.layers = []

    def add_layer(self, layer):

        self.layers.append(layer)

    def remove_layer(self, layer):

        if layer in self.layers:
            self.layers.remove(layer)

    def clear(self):

        self.layers.clear()

    def count(self):

        return len(self.layers)
EOF

#######################################################
# Tests
#######################################################

cat > "$PROJECT/tests/test_map_engine.py" << 'EOF'
from acf.maps.map_engine import MapEngine


def test_map_engine():

    engine = MapEngine()

    assert engine.count() == 0

    engine.add_layer("temperature")

    assert engine.count() == 1

    engine.clear()

    assert engine.count() == 0
EOF

echo
echo "Cartography Engine created successfully."
