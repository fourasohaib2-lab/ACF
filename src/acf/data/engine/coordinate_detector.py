"""
Atmospheric Complexity Framework (ACF)

Coordinate Detector
"""

from __future__ import annotations


class CoordinateDetector:
    """
    Détecte automatiquement les coordonnées d'un Dataset.
    """

    LAT_NAMES = {"lat", "latitude", "y"}
    LON_NAMES = {"lon", "longitude", "x"}
    TIME_NAMES = {"time", "valid_time", "forecast_time"}
    LEVEL_NAMES = {"level", "pressure", "isobaric", "height"}

    ###########################################################

    def detect(self, dataset):

        dimensions = {
            d.lower() for d in getattr(dataset, "dimensions", [])
        }

        return {
            "latitude": self._find(dimensions, self.LAT_NAMES),
            "longitude": self._find(dimensions, self.LON_NAMES),
            "time": self._find(dimensions, self.TIME_NAMES),
            "level": self._find(dimensions, self.LEVEL_NAMES),
        }

    ###########################################################

    def _find(self, dimensions, aliases):

        for alias in aliases:
            if alias in dimensions:
                return alias

        return None
