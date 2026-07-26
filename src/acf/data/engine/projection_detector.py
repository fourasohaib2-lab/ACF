"""
Atmospheric Complexity Framework (ACF)

Projection Detector
"""

from __future__ import annotations


class ProjectionDetector:
    """
    Détection automatique de la projection cartographique.
    Compatible avec :
      - un dictionnaire de métadonnées
      - un objet Dataset
    """

    PROJECTIONS = {
        "latitude_longitude": "latlon",
        "latlon": "latlon",
        "mercator": "mercator",
        "lambert_conformal_conic": "lambert",
        "lambert": "lambert",
        "polar_stereographic": "polar",
        "stereographic": "polar",
    }

    ###########################################################

    def detect(self, obj):

        # Cas 1 : dictionnaire
        if isinstance(obj, dict):

            grid = obj.get("grid_mapping_name")

            if grid is None:
                return "unknown"

            return self.PROJECTIONS.get(grid.lower(), "unknown")

        # Cas 2 : Dataset
        metadata = getattr(obj, "metadata", {})
        dimensions = {d.lower() for d in getattr(obj, "dimensions", [])}

        grid = metadata.get("grid_mapping_name") or metadata.get("projection")

        if grid:
            return self.PROJECTIONS.get(grid.lower(), grid)

        if {"latitude", "longitude"} <= dimensions:
            return "EPSG:4326"

        if {"lat", "lon"} <= dimensions:
            return "EPSG:4326"

        if {"x", "y"} <= dimensions:
            return "Projected"

        return "unknown"

    ###########################################################

    def is_geographic(self, obj):

        projection = self.detect(obj)

        return projection in ("EPSG:4326", "latlon")
