"""
Atmospheric Complexity Framework (ACF)

VerticalAxis
============

Represents the vertical coordinate of a 4D atmospheric field.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from uuid import uuid4


class VerticalAxis:
    """
    Vertical axis.
    """

    def __init__(self):

        self.id = str(uuid4())

        self.levels = []

        self.unit = "hPa"

        self.axis_type = "pressure"

        self.metadata = {}

        self.validated = False

        self.errors = []

        self.created = datetime.now().isoformat()

        self.modified = self.created

    ##################################################

    def add(self, level):

        self.levels.append(level)

        self.touch()

        return level

    ##################################################

    def remove(self, level):

        if level in self.levels:
            self.levels.remove(level)

            self.touch()

    ##################################################

    def clear(self):

        self.levels.clear()

        self.touch()

    ##################################################

    def touch(self):

        self.modified = datetime.now().isoformat()

    ##################################################

    @property
    def first(self):

        if not self.levels:
            return None

        return self.levels[0]

    ##################################################

    @property
    def last(self):

        if not self.levels:
            return None

        return self.levels[-1]

    ##################################################

    @property
    def count(self):

        return len(self.levels)

    ##################################################

    def validate(self):

        self.errors = []

        if not self.levels:
            self.errors.append("Vertical axis is empty.")

        self.validated = len(self.errors) == 0

        return self.validated

    ##################################################

    def copy(self):

        return deepcopy(self)

    ##################################################

    def summary(self):

        return {
            "count": self.count,
            "first": self.first,
            "last": self.last,
            "unit": self.unit,
            "axis_type": self.axis_type,
            "validated": self.validated,
        }

    ##################################################

    def __len__(self):

        return len(self.levels)

    ##################################################

    def __repr__(self):

        return f"VerticalAxis(levels={len(self.levels)}, unit='{self.unit}')"
