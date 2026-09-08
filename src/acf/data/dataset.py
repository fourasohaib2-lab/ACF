"""
Atmospheric Complexity Framework (ACF)

Dataset Core Object
===================

Internal representation of meteorological datasets.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


class Dataset:
    """
    Generic meteorological dataset.
    """

    ##################################################

    def __init__(
        self,
        name: str = "",
        filepath: Path | None = None,
        filetype: str = "",
        source: str = "",
    ):

        #
        # Identity
        #

        self.id = str(uuid4())

        self.name = name

        self.source = source

        #
        # File information
        #

        self.filepath = filepath

        self.filetype = filetype

        #
        # Containers
        #

        self.variables: dict[str, Any] = {}

        self.dimensions: dict[str, Any] = {}

        self.metadata: dict[str, Any] = {}

        self.attributes = self.metadata

        #
        # Validation
        #

        self.validated = False

        self.errors: list[Any] = []

        #
        # Dates
        #

        self.created = datetime.now(timezone.utc).isoformat()

        self.modified = self.created

    ##################################################
    # Variables
    ##################################################

    def add_variable(
        self,
        name: str,
        value=None,
    ):

        self.variables[name] = value

        self.touch()

    ##################################################

    def get_variable(
        self,
        name: str,
    ):

        return self.variables.get(name)

    ##################################################

    def has_variable(
        self,
        name: str,
    ):

        return name in self.variables

    ##################################################

    def remove_variable(
        self,
        name: str,
    ):

        self.variables.pop(name, None)

        self.touch()

    ##################################################
    # Dimensions
    ##################################################

    def add_dimension(
        self,
        name: str,
        size: int | None,
    ):

        self.dimensions[name] = size

        self.touch()

    ##################################################
    # Compatibility with tests
    ##################################################

    def set_dimension(
        self,
        name: str,
        size: int,
    ):
        """
        Compatibility API.

        Equivalent to add_dimension().
        """

        self.add_dimension(name, size)

        return size

    ##################################################

    def get_dimension(
        self,
        name: str,
    ):

        return self.dimensions.get(name)

    ##################################################

    def has_dimension(
        self,
        name: str,
    ):

        return name in self.dimensions

    ##################################################

    def remove_dimension(
        self,
        name: str,
    ):

        self.dimensions.pop(name, None)

        self.touch()

    ##################################################
    # Metadata & Attributes
    ##################################################

    def set_metadata(
        self,
        name: str,
        value,
    ):

        self.metadata[name] = value

        self.touch()

    ##################################################

    def get_metadata(
        self,
        name: str,
    ):

        return self.metadata.get(name)

    ##################################################

    def has_metadata(
        self,
        name: str,
    ) -> bool:

        return name in self.metadata

    ##################################################

    def set_attribute(
        self,
        name: str,
        value,
    ):

        self.attributes[name] = value

        self.touch()

    ##################################################

    def get_attribute(
        self,
        name: str,
    ):

        return self.attributes.get(name)

    ##################################################

    def has_attribute(
        self,
        name: str,
    ) -> bool:

        return name in self.attributes

    ##################################################
    # Validation
    ##################################################

    def validate(self):

        self.errors = []

        if not self.name:
            self.errors.append("Dataset name missing")

        if not self.variables:
            self.errors.append("No variables found")

        self.validated = len(self.errors) == 0

        return self.validated

    ##################################################
    # Utilities
    ##################################################

    def touch(self):

        self.modified = datetime.now(timezone.utc).isoformat()

    ##################################################

    @property
    def variable_names(self):

        return list(self.variables.keys())

    ##################################################

    @property
    def dimension_names(self):

        return list(self.dimensions.keys())

    ##################################################

    def summary(self):

        return {
            "id": self.id,
            "name": self.name,
            "source": self.source,
            "filetype": self.filetype,
            "variables": self.variable_names,
            "dimensions": self.dimension_names,
            "validated": self.validated,
            "errors": self.errors,
        }

    ##################################################

    def __len__(self):

        return len(self.variables)

    ##################################################

    def __repr__(self):

        return f"Dataset(name='{self.name}', type='{self.filetype}', variables={len(self.variables)})"
