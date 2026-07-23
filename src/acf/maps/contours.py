"""
Atmospheric Complexity Framework (ACF)
Contour Engine
=====================================

Contour level manager.
"""


class Contours:
    """Manage contour levels."""

    def __init__(self):
        self._levels = {}

    def set_levels(self, variable: str, levels):
        """Store contour levels."""
        self._levels[variable] = list(levels)

    def get_levels(self, variable: str):
        """Return contour levels."""
        return self._levels.get(variable)

    def exists(self, variable: str):
        """Check whether levels exist."""
        return variable in self._levels

    def remove(self, variable: str):
        """Remove contour levels."""
        self._levels.pop(variable, None)

    def variables(self):
        """Return variables having contour levels."""
        return sorted(self._levels.keys())

    def clear(self):
        """Remove all contour definitions."""
        self._levels.clear()

    def count(self):
        """Return number of contour definitions."""
        return len(self._levels)
