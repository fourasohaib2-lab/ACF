"""
Atmospheric Complexity Framework (ACF)

Grid4D
======

Represents the spatial and temporal grid of a 4D atmospheric field.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from uuid import uuid4


class Grid4D:
    """
    Four-dimensional grid.
    """

    def __init__(self):

        self.id = str(uuid4())

        self.time = None

        self.vertical = None

        self.latitudes = []

        self.longitudes = []

        self.projection = "EPSG:4326"

        self.metadata = {}

        self.validated = False

        self.errors = []

        self.created = datetime.now().isoformat()

        self.modified = self.created

    ##################################################

    def set_time_axis(self, axis):

        self.time = axis

        self.touch()

    ##################################################

    def set_vertical_axis(self, axis):

        self.vertical = axis

        self.touch()

    ##################################################

    def set_latitudes(self, values):

        self.latitudes = list(values)

        self.touch()

    ##################################################

    def set_longitudes(self, values):

        self.longitudes = list(values)

        self.touch()

    ##################################################

    def touch(self):

        self.modified = datetime.now().isoformat()

    ##################################################

    def validate(self):

        self.errors = []

        if self.time is None:
            self.errors.append("Missing time axis.")

        if self.vertical is None:
            self.errors.append("Missing vertical axis.")

        if not self.latitudes:
            self.errors.append("Missing latitudes.")

        if not self.longitudes:
            self.errors.append("Missing longitudes.")

        self.validated = len(self.errors) == 0

        return self.validated

    ##################################################

    def copy(self):

        return deepcopy(self)

    ##################################################

    def summary(self):

        return {
            "latitudes": len(self.latitudes),
            "longitudes": len(self.longitudes),
            "projection": self.projection,
            "validated": self.validated,
        }

    ##################################################

    def __repr__(self):

        return f"Grid4D(lat={len(self.latitudes)}, lon={len(self.longitudes)})"
