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
