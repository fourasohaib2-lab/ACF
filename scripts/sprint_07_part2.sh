#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

echo "========================================="
echo " ACF Sprint 07 - Part 2"
echo " Layer Engine"
echo "========================================="

####################################################
# BASE LAYER
####################################################

cat > "$PROJECT/src/acf/maps/layers/base_layer.py" << 'EOF'
"""
Base Layer
"""

class BaseLayer:

    def __init__(self, name):

        self.name = name
        self.visible = True
        self.opacity = 1.0

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def set_opacity(self, value):

        value = float(value)

        if value < 0:
            value = 0

        if value > 1:
            value = 1

        self.opacity = value
EOF

####################################################
# RASTER LAYER
####################################################

cat > "$PROJECT/src/acf/maps/layers/raster_layer.py" << 'EOF'
"""
Raster Layer
"""

from acf.maps.layers.base_layer import BaseLayer


class RasterLayer(BaseLayer):

    def __init__(self, name, dataset=None):

        super().__init__(name)

        self.dataset = dataset
EOF

####################################################
# VECTOR LAYER
####################################################

cat > "$PROJECT/src/acf/maps/layers/vector_layer.py" << 'EOF'
"""
Vector Layer
"""

from acf.maps.layers.base_layer import BaseLayer


class VectorLayer(BaseLayer):

    def __init__(self, name):

        super().__init__(name)

        self.features = []
EOF

####################################################
# LAYER MANAGER
####################################################

cat > "$PROJECT/src/acf/maps/layer_manager.py" << 'EOF'
"""
Layer Manager
"""

class LayerManager:

    def __init__(self):

        self.layers = []

    def add(self, layer):

        self.layers.append(layer)

    def remove(self, layer):

        if layer in self.layers:
            self.layers.remove(layer)

    def clear(self):

        self.layers.clear()

    def count(self):

        return len(self.layers)

    def names(self):

        return [layer.name for layer in self.layers]
EOF

####################################################
# TESTS
####################################################

cat > "$PROJECT/tests/test_layer_manager.py" << 'EOF'
from acf.maps.layer_manager import LayerManager
from acf.maps.layers.base_layer import BaseLayer


def test_layer_manager():

    manager = LayerManager()

    assert manager.count() == 0

    manager.add(BaseLayer("Temperature"))

    assert manager.count() == 1

    assert manager.names() == ["Temperature"]

    manager.clear()

    assert manager.count() == 0
EOF

echo
echo "Layer Engine installed successfully."
