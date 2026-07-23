"""
Atmospheric Complexity Framework (ACF)
ColorMap Engine
=====================================

Color map manager.
"""


class ColorMap:
    """Manage meteorological color maps."""

    def __init__(self):
        self._maps = {
            "temperature": "coolwarm",
            "pressure": "viridis",
            "humidity": "Blues",
            "precipitation": "YlGnBu",
            "wind": "plasma",
            "reflectivity": "turbo",
            "cape": "inferno",
            "terrain": "terrain",
            "clouds": "Greys",
            "satellite": "gray",
        }

    def available(self):
        """Return available color maps."""
        return sorted(self._maps.keys())

    def get(self, name):
        """Return a color map."""
        return self._maps.get(name)

    def exists(self, name):
        """Check if a color map exists."""
        return name in self._maps

    def add(self, name, cmap):
        """Add a new color map."""
        self._maps[name] = cmap

    def remove(self, name):
        """Remove a color map."""
        if name in self._maps:
            del self._maps[name]

    def count(self):
        """Return number of color maps."""
        return len(self._maps)
