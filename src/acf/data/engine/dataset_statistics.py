"""
Atmospheric Complexity Framework (ACF)

Dataset Statistics

Scientific statistics computed on Dataset variables.
"""

from __future__ import annotations

import math


class DatasetStatistics:
    """
    Compute simple statistics on dataset variables.
    """

    def __init__(self, dataset):

        self.dataset = dataset

    ##########################################################

    @staticmethod
    def _numeric(values):

        result = []

        for value in values:

            if isinstance(value, (int, float)):

                if math.isnan(value):
                    continue

                result.append(float(value))

        return result

    ##########################################################

    def compute(self):

        statistics = {}

        for name, values in self.dataset.variables.items():

            if not isinstance(values, (list, tuple)):
                continue

            numeric = self._numeric(values)

            if not numeric:

                continue

            statistics[name] = {

                "count": len(numeric),

                "minimum": min(numeric),

                "maximum": max(numeric),

                "mean": sum(numeric) / len(numeric),

            }

        return statistics

