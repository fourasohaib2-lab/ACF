"""
Atmospheric Complexity Framework (ACF)
Exporter Engine
===============================
"""

from pathlib import Path


class Exporter:
    """Manage map exports."""

    def __init__(self):
        self._exports = []

    def export(self, filename):
        filename = Path(filename)
        self._exports.append(filename)
        return filename

    def exists(self, filename):
        filename = Path(filename)
        return filename in self._exports

    def remove(self, filename):
        filename = Path(filename)
        if filename in self._exports:
            self._exports.remove(filename)

    def clear(self):
        self._exports.clear()

    def count(self):
        return len(self._exports)

    def exports(self):
        return list(self._exports)

    def __repr__(self):
        return f"Exporter(count={len(self._exports)})"
