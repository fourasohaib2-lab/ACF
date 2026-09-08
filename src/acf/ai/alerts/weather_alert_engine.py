"""
Weather Alert Engine
"""

import numpy as np


class WeatherAlertEngine:
    def __init__(self):

        self.rules = []

    ##################################################

    def register_rule(self, variable, threshold, level, message):

        self.rules.append({"variable": variable, "threshold": threshold, "level": level, "message": message})

    ##################################################

    def analyze(self, dataset):

        alerts = []

        for rule in self.rules:
            variable = rule["variable"]

            if variable not in dataset:
                continue

            values = np.asarray(dataset[variable])

            maximum = float(np.nanmax(values))

            if maximum >= rule["threshold"]:
                alerts.append(
                    {"variable": variable, "level": rule["level"], "value": maximum, "message": rule["message"]}
                )

        return alerts
