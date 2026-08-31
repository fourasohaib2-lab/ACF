"""
ACF Map Engine (Canonical Implementation)
"""


class MapEngine:
    def __init__(self):
        self.layers = []
        self.figures = []
        self.current_projection = "PlateCarree"

    def add_layer(self, layer):
        self.layers.append(layer)

    def remove_layer(self, layer):
        if layer in self.layers:
            self.layers.remove(layer)

    def clear_layers(self):
        self.layers.clear()

    def clear(self):
        self.clear_layers()

    def layer_count(self):
        return len(self.layers)

    def count(self):
        return self.layer_count()

    def set_projection(self, projection):
        self.current_projection = projection

    def get_projection(self):
        return self.current_projection
