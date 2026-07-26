"""
Atmospheric Complexity Framework (ACF)

Grid Detector
"""

from __future__ import annotations


class GridDetector:
    """
    Détection automatique du type de grille.
    """

    ###########################################################

    def detect(self, dataset):

        metadata = getattr(dataset, "metadata", {})

        grid = metadata.get("grid", "")

        if grid:
            return grid

        dims = set(getattr(dataset, "dimensions", []))

        if {"latitude", "longitude"} <= dims:
            return "Regular Lat/Lon"

        if {"lat", "lon"} <= dims:
            return "Regular Lat/Lon"

        if {"x", "y"} <= dims:
            return "Projected Grid"

        return "Unknown"

    ###########################################################

    def is_regular(self, dataset):

        return self.detect(dataset) == "Regular Lat/Lon"
