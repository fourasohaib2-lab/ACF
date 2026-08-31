"""
Atmospheric Complexity Framework (ACF)

Data Integration Engine
"""

from __future__ import annotations

from pathlib import Path

from acf.data.dataset import Dataset


class IntegrationEngine:
    """
    Central engine responsible for integrating
    meteorological datasets into the ACF format.
    """

    def __init__(self):

        self.dataset = None

    ###########################################################

    def load(self, dataset: Dataset):

        self.dataset = dataset

        return dataset

    ###########################################################

    def create_dataset(
        self,
        name: str,
        filepath,
        filetype: str,
    ):

        dataset = Dataset(
            name=name,
            filepath=Path(filepath),
            filetype=filetype,
        )

        self.dataset = dataset

        return dataset

    ###########################################################

    @property
    def loaded(self):

        return self.dataset is not None

    ###########################################################

    def unload(self):

        self.dataset = None

    ###########################################################

    def summary(self):

        if not self.loaded:
            return {}

        return {
            "name": self.dataset.name,
            "filetype": self.dataset.filetype,
            "filepath": str(self.dataset.filepath),
            "variables": len(self.dataset.variables),
            "dimensions": len(self.dataset.dimensions),
            "metadata": len(self.dataset.metadata),
        }
