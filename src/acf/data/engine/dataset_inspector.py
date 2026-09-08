"""
Atmospheric Complexity Framework (ACF)

Dataset Inspector
"""

from __future__ import annotations


class DatasetInspector:
    """
    Inspect a Dataset and return a structured report.
    """

    def __init__(self, dataset):
        self.dataset = dataset

    def inspect(self):

        return {
            "name": self.dataset.name,
            "variables": len(self.dataset.variables),
            "dimensions": len(self.dataset.dimensions),
            "metadata": len(self.dataset.metadata),
            "validated": self.dataset.validated,
            "variable_names": list(self.dataset.variables.keys()),
            "dimension_names": list(self.dataset.dimensions.keys()),
            "metadata_keys": list(self.dataset.metadata.keys()),
        }
