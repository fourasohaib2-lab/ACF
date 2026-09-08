"""
Atmospheric Complexity Framework (ACF)

Dataset Metadata Extractor
"""

from __future__ import annotations


class DatasetMetadata:
    """
    Extraction des métadonnées d'un Dataset.
    """

    ############################################################

    def extract(self, dataset):

        return {
            "name": getattr(dataset, "name", ""),
            "model": dataset.metadata.get("model", ""),
            "institution": dataset.metadata.get("institution", ""),
            "source": dataset.metadata.get("source", ""),
            "history": dataset.metadata.get("history", ""),
            "references": dataset.metadata.get("references", ""),
            "variables": len(dataset.variables),
            "dimensions": len(dataset.dimensions),
        }

    ############################################################

    def has_metadata(self, dataset):

        return len(dataset.metadata) > 0
