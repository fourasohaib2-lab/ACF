"""
Metadata Inspector
"""


class MetadataInspector:

    def inspect(self, dataset):

        info = {
            "name": dataset.name,
            "filetype": dataset.filetype,
            "filepath": str(dataset.filepath),
            "variables": [],
            "dimensions": {},
            "metadata": {},
            "summary": {}
        }

        # Variables
        if hasattr(dataset, "variables"):
            info["variables"] = list(dataset.variables)

        # Dimensions
        if hasattr(dataset, "dimensions"):
            info["dimensions"] = dict(dataset.dimensions)

        # Métadonnées
        if hasattr(dataset, "metadata"):
            info["metadata"] = dict(dataset.metadata)

        # Résumé
        info["summary"] = {
            "variable_count": len(info["variables"]),
            "dimension_count": len(info["dimensions"]),
            "metadata_count": len(info["metadata"]),
        }

        return info
