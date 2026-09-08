"""
Atmospheric Complexity Framework (ACF)

Dataset Classifier
"""

from __future__ import annotations


class DatasetClassifier:
    """
    Classifie automatiquement les jeux de données.
    """

    MODEL_MAP = {
        "ERA5": "Reanalysis",
        "ERA-INTERIM": "Reanalysis",
        "WRF": "Regional NWP",
        "AROME": "Mesoscale NWP",
        "ARPEGE": "Global NWP",
        "IFS": "Global NWP",
        "ICON": "Global NWP",
        "GFS": "Global NWP",
        "GEFS": "Ensemble",
        "ECENS": "Ensemble",
        "METEOSAT": "Satellite",
        "GOES": "Satellite",
        "SENTINEL": "Satellite",
        "RADAR": "Radar",
        "BUOY": "Ocean Observation",
        "STATION": "Surface Observation",
    }

    ############################################################

    def classify(self, dataset):

        model = ""

        if hasattr(dataset, "metadata"):
            model = dataset.metadata.get("model", "")

        model = model.upper()

        return self.MODEL_MAP.get(model, "Unknown")
