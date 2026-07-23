"""
ColorBar Manager
================
"""


class ColorBarManager:

    def __init__(self):

        self._bars = {}

    def add(self, name, colorbar):

        self._bars[name] = colorbar

    def get(self, name):

        return self._bars.get(name)

    def remove(self, name):

        self._bars.pop(name, None)

    def exists(self, name):

        return name in self._bars

    def names(self):

        return sorted(self._bars.keys())

    def count(self):

        return len(self._bars)

    def clear(self):

        self._bars.clear()

    def __repr__(self):

        return f"ColorBarManager(count={self.count()})"
