"""
Atmospheric Complexity Framework (ACF)
Shapefile Manager
======================================
"""

from pathlib import Path


class ShapeFileManager:
    """Gestion des couches Shapefile."""

    def __init__(self):
        self._layers = {}

    def add(self, name: str, filename):
        self._layers[name] = Path(filename)

    def get(self, name: str):
        return self._layers.get(name)

    def exists(self, name: str):
        return name in self._layers

    def remove(self, name: str):
        self._layers.pop(name, None)

    def clear(self):
        self._layers.clear()

    def count(self):
        return len(self._layers)

    def names(self):
        return sorted(self._layers.keys())

    @property
    def layers(self):
        return self._layers

    def __len__(self):
        return len(self._layers)

    def __repr__(self):
        return f"ShapeFileManager({len(self._layers)} layers)"

