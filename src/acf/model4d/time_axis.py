"""
Atmospheric Complexity Framework (ACF)

TimeAxis
========

Represents the temporal axis of a 4D atmospheric field.
"""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4
from copy import deepcopy


class TimeAxis:
    """
    Time axis for atmospheric datasets.
    """

    ##################################################

    def __init__(self):

        self.id = str(uuid4())

        self.times = []

        self.metadata = {}

        self.validated = False

        self.errors = []

        self.created = datetime.now().isoformat()

        self.modified = self.created

    ##################################################

    def add(self, value):

        if isinstance(value, str):
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))

        self.times.append(value)

        self.touch()

        return value

    ##################################################

    def remove(self, value):

        if value in self.times:
            self.times.remove(value)

            self.touch()

    ##################################################

    def clear(self):

        self.times.clear()

        self.touch()

    ##################################################

    def touch(self):

        self.modified = datetime.now().isoformat()

    ##################################################

    @property
    def first(self):

        if not self.times:
            return None

        return self.times[0]

    ##################################################

    @property
    def last(self):

        if not self.times:
            return None

        return self.times[-1]

    ##################################################

    @property
    def step(self):

        if len(self.times) < 2:
            return None

        return self.times[1] - self.times[0]

    ##################################################

    @property
    def step_hours(self):

        if self.step is None:
            return None

        return self.step.total_seconds() / 3600

    ##################################################

    def validate(self):

        self.errors = []

        if len(self.times) == 0:
            self.errors.append("Time axis is empty.")

        self.validated = len(self.errors) == 0

        return self.validated

    ##################################################

    def copy(self):

        return deepcopy(self)

    ##################################################

    def summary(self):

        return {

            "count": len(self.times),

            "first": self.first,

            "last": self.last,

            "step_hours": self.step_hours,

            "validated": self.validated,

        }

    ##################################################

    def __len__(self):

        return len(self.times)

    ##################################################

    def __repr__(self):

        return f"TimeAxis({len(self.times)} times)"
