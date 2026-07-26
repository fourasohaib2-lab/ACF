"""
Atmospheric Complexity Framework (ACF)

Data Fusion Engine
"""

from copy import deepcopy


class DataFusionEngine:
    """
    Merge multiple datasets into one.
    """

    def merge(self, *datasets):

        if not datasets:
            raise ValueError("No datasets supplied.")

        result = deepcopy(datasets[0])

        for dataset in datasets[1:]:

            # Variables
            if hasattr(result, "variables") and hasattr(dataset, "variables"):
                result.variables.update(dataset.variables)

            # Metadata
            if hasattr(result, "metadata") and hasattr(dataset, "metadata"):
                result.metadata.update(dataset.metadata)

            # Dimensions
            if hasattr(result, "dimensions") and hasattr(dataset, "dimensions"):
                result.dimensions.update(dataset.dimensions)

        return result
