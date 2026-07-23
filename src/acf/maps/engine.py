"""
Atmospheric Complexity Framework (ACF)
Map Engine
=====================================

Main mapping engine.
"""


class MapEngine:
    """Main map engine."""

    def __init__(self):
        self.layers = []
        self.figures = []
        self.current_projection = "PlateCarree"

    def add_layer(self, layer):
        """Add a map layer."""
        self.layers.append(layer)

    def remove_layer(self, layer):
        """Remove a map layer."""
        if layer in self.layers:
            self.layers.remove(layer)

    def clear_layers(self):
        """Remove all layers."""
        self.layers.clear()

    def layer_count(self):
        """Return the number of layers."""
        return len(self.layers)

    def set_projection(self, projection):
        """Set current projection."""
        self.current_projection = projection

    def get_projection(self):
        """Return current projection."""
        return self.current_projection

