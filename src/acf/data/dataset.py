"""
Atmospheric Complexity Framework (ACF)
Dataset
=====================================

Generic meteorological dataset.
"""

from pathlib import Path


class Dataset:
    """Generic meteorological dataset."""

    def __init__(
        self,
        name: str = "",
        filepath: Path | None = None,
        filetype: str = "",
    ):
        self.name = name
        self.filepath = filepath
        self.filetype = filetype

        self.variables = {}
        self.dimensions = {}

        # Métadonnées
        self.metadata = {}

        # Alias de compatibilité
        self.attributes = self.metadata

    # ======================================================
    # Variables
    # ======================================================

    def add_variable(self, name: str, value=None):
        self.variables[name] = value

    def get_variable(self, name: str):
        return self.variables.get(name)

    def has_variable(self, name: str):
        return name in self.variables

    def remove_variable(self, name: str):
        self.variables.pop(name, None)

    # ======================================================
    # Dimensions
    # ======================================================

    def add_dimension(self, name: str, size: int):
        self.dimensions[name] = size

    def set_dimension(self, name: str, size: int):
        self.dimensions[name] = size

    def get_dimension(self, name: str):
        return self.dimensions.get(name)

    def has_dimension(self, name: str):
        return name in self.dimensions

    # ======================================================
    # Metadata
    # ======================================================

    def set_metadata(self, name: str, value):
        self.metadata[name] = value

    def get_metadata(self, name: str):
        return self.metadata.get(name)

    def has_metadata(self, name: str):
        return name in self.metadata

    def remove_metadata(self, name: str):
        self.metadata.pop(name, None)

    # Compatibilité

    def add_attribute(self, name: str, value):
        self.set_metadata(name, value)

    def get_attribute(self, name: str):
        return self.get_metadata(name)

    # ======================================================
    # Informations
    # ======================================================

    @property
    def variable_names(self):
        return list(self.variables.keys())

    @property
    def dimension_names(self):
        return list(self.dimensions.keys())

    @property
    def metadata_names(self):
        return list(self.metadata.keys())

    def summary(self):
        return {
            "name": self.name,
            "filepath": str(self.filepath) if self.filepath else None,
            "filetype": self.filetype,
            "variables": self.variable_names,
            "dimensions": self.dimension_names,
            "metadata": self.metadata_names,
        }

    def __len__(self):
        return len(self.variables)

    def __contains__(self, item):
        return item in self.variables

    def __repr__(self):
        return (
            f"Dataset(name='{self.name}', "
            f"filetype='{self.filetype}', "
            f"variables={len(self.variables)}, "
            f"dimensions={len(self.dimensions)}, "
            f"metadata={len(self.metadata)})"
        )

