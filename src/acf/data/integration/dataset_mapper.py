"""
Atmospheric Complexity Framework (ACF)

Dataset Mapper
"""

from __future__ import annotations

from acf.data.dataset import Dataset


class DatasetMapper:
    """
    Dataset mapper.
    """

    def map(self, dataset: Dataset) -> Dataset:
        """
        Map one dataset into another Dataset object.
        """

        return self.copy(dataset)

    ##########################################################

    def copy(self, dataset: Dataset) -> Dataset:

        copied = Dataset(
            name=dataset.name,
            filepath=dataset.filepath,
            filetype=dataset.filetype,
        )

        copied.variables = dict(dataset.variables)
        copied.dimensions = dict(dataset.dimensions)
        copied.metadata = dict(dataset.metadata)
        copied.validated = dataset.validated

        return copied
