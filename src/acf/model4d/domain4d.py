"""
Atmospheric Complexity Framework (ACF)

Domain4D
========

Represents a complete atmospheric domain.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from uuid import uuid4


class Domain4D:
    def __init__(self):

        self.id = str(uuid4())

        self.name = ""

        self.model = ""

        self.grid = None

        self.resolution = ""

        self.projection = "EPSG:4326"

        self.west = None
        self.east = None
        self.south = None
        self.north = None

        self.start_time = None
        self.end_time = None

        self.metadata = {}

        self.validated = False

        self.errors = []

        self.created = datetime.now().isoformat()

        self.modified = self.created

    ##################################################

    def set_grid(self, grid):

        self.grid = grid

        self.touch()

    ##################################################

    def touch(self):

        self.modified = datetime.now().isoformat()

    ##################################################

    def validate(self):

        self.errors = []

        if self.grid is None:
            self.errors.append("Missing grid.")

        if self.name == "":
            self.errors.append("Missing domain name.")

        self.validated = len(self.errors) == 0

        return self.validated

    ##################################################

    def copy(self):

        return deepcopy(self)

    ##################################################

    def summary(self):

        return {
            "name": self.name,
            "model": self.model,
            "projection": self.projection,
            "resolution": self.resolution,
            "validated": self.validated,
        }

    ##################################################

    def __repr__(self):

        return f"Domain4D(name='{self.name}', model='{self.model}')"
