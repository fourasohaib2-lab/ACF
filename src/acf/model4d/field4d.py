"""
Atmospheric Complexity Framework (ACF)

Field4D
========

Represents a four-dimensional atmospheric field.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from uuid import uuid4


class Field4D:

    def __init__(self):

        self.id = str(uuid4())

        self.name = ""

        self.unit = ""

        self.domain = None

        self.values = None

        self.metadata = {}

        self.attributes = self.metadata

        self.validated = False

        self.errors = []

        self.created = datetime.now().isoformat()

        self.modified = self.created

    ##################################################

    def set_domain(self, domain):

        self.domain = domain

        self.touch()

    ##################################################

    def set_values(self, values):

        self.values = values

        self.touch()

    ##################################################

    def touch(self):

        self.modified = datetime.now().isoformat()

    ##################################################

    def validate(self):

        self.errors = []

        if self.name == "":
            self.errors.append("Missing field name.")

        if self.domain is None:
            self.errors.append("Missing domain.")

        if self.values is None:
            self.errors.append("Missing values.")

        self.validated = len(self.errors) == 0

        return self.validated

    ##################################################

    def copy(self):

        return deepcopy(self)

    ##################################################

    def summary(self):

        return {

            "name": self.name,

            "unit": self.unit,

            "validated": self.validated,

            "metadata": len(self.metadata),

        }

    ##################################################

    def __repr__(self):

        return (

            f"Field4D(name='{self.name}', "

            f"unit='{self.unit}')"

        )
