"""
Dataset Analyzer
"""

import numpy as np


class DatasetAnalyzer:
    """
    Analyse un ensemble de variables météorologiques.
    """

    def analyze(self, dataset):

        report = {}

        for name, values in dataset.items():
            array = np.asarray(values)

            report[name] = {
                "shape": array.shape,
                "dtype": str(array.dtype),
                "min": float(np.nanmin(array)),
                "max": float(np.nanmax(array)),
                "mean": float(np.nanmean(array)),
            }

        return report

    ##################################################

    def variables(self, dataset):

        return sorted(dataset.keys())

    ##################################################

    def summary(self, dataset):

        return {
            "variables": self.variables(dataset),
            "count": len(dataset),
        }
