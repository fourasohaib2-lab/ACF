"""
Atmospheric Complexity Framework (ACF)

Dataset Engine
"""

from __future__ import annotations

from pathlib import Path

from acf.data.dataset import Dataset


class DatasetEngine:
    """
    Main dataset engine.
    """

    def __init__(self):
        self.dataset = None

    ##########################################################

    def create_dataset(
        self,
        name: str,
        filepath: Path | None = None,
        filetype: str = "",
        source: str = "",
    ) -> Dataset:
        """
        Create a Dataset instance and load it into the engine.
        """

        dataset = Dataset(
            name=name,
            filepath=filepath,
            filetype=filetype,
            source=source,
        )

        self.dataset = dataset

        return dataset

    ##########################################################

    def load(self, dataset: Dataset) -> Dataset:
        self.dataset = dataset
        return dataset

    ##########################################################

    @property
    def loaded(self) -> bool:
        return self.dataset is not None

    ##########################################################

    def variable_count(self) -> int:
        return 0 if not self.loaded else len(self.dataset.variables)

    ##########################################################

    def dimension_count(self) -> int:
        return 0 if not self.loaded else len(self.dataset.dimensions)

    ##########################################################

    def metadata_count(self) -> int:
        return 0 if not self.loaded else len(self.dataset.metadata)

    ##########################################################

    def summary(self) -> dict:
        if not self.loaded:
            return {}

        return {
            "name": self.dataset.name,
            "variables": self.variable_count(),
            "dimensions": self.dimension_count(),
            "metadata": self.metadata_count(),
            "validated": self.dataset.validated,
        }

    ##########################################################

    def clear(self):
        self.dataset = None
