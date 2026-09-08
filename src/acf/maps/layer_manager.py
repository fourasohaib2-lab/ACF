"""
Layer Manager
=============

Gestionnaire des couches cartographiques.
"""


class LayerManager:
    def __init__(self):
        self.layers = {}

    def add(self, layer):
        self.layers[layer.name] = layer

    def remove(self, name):
        self.layers.pop(name, None)

    def get(self, name):
        return self.layers.get(name)

    def exists(self, name):
        return name in self.layers

    def clear(self):
        self.layers.clear()

    def names(self):
        return list(self.layers.keys())

    def count(self):
        return len(self.layers)

    def hide(self, name):
        layer = self.get(name)
        if layer:
            layer.set_visible(False)

    def show(self, name):
        layer = self.get(name)
        if layer:
            layer.set_visible(True)

    def __repr__(self):
        return f"LayerManager(count={len(self.layers)})"
