"""
Atmospheric Complexity Framework (ACF)
Projection Engine
=====================================

Map projection manager.
"""


class Projection:
    """Projection manager."""

    def __init__(self):
        self._projections = [
            "PlateCarree",
            "Mercator",
            "LambertConformal",
            "LambertAzimuthalEqualArea",
            "Orthographic",
            "Robinson",
            "Mollweide",
            "PolarStereo",
            "Geostationary",
        ]

        self._current = "PlateCarree"

    def set(self, projection: str):
        if projection not in self._projections:
            raise ValueError(f"Unknown projection: {projection}")

        self._current = projection

    def current(self):
        return self._current

    def available(self):
        return self._projections.copy()

    def exists(self, projection: str):
        return projection in self._projections

    def count(self):
        return len(self._projections)

    def reset(self):
        self._current = "PlateCarree"

