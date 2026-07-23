"""
Colormap Manager
================
"""


class ColormapManager:

    def __init__(self):

        self._maps = {}

    def add(self, name, colormap):

        self._maps[name] = colormap

    def get(self, name):

        return self._maps.get(name)

    def remove(self, name):

        self._maps.pop(name, None)

    def exists(self, name):

        return name in self._maps

    def names(self):

        return sorted(self._maps.keys())

    def count(self):

        return len(self._maps)

    def clear(self):

        self._maps.clear()

    def __repr__(self):

        return f"ColormapManager(count={self.count()})"
