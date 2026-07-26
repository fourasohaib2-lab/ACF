"""
Atmospheric Complexity Framework (ACF)

Interpolation Engine
====================
"""

from copy import deepcopy


class InterpolationEngine:

    def __init__(self):

        self.algorithm = "nearest"

    ##################################################

    def nearest(self, values):

        return deepcopy(values)

    ##################################################

    def linear(self, values):

        return deepcopy(values)

    ##################################################

    def bilinear(self, values):

        return deepcopy(values)

    ##################################################

    def interpolate(
        self,
        values,
        method="nearest",
    ):

        if method == "nearest":
            return self.nearest(values)

        if method == "linear":
            return self.linear(values)

        if method == "bilinear":
            return self.bilinear(values)

        raise ValueError(f"Unknown interpolation method: {method}")

    ##################################################

    def available_methods(self):

        return [

            "nearest",

            "linear",

            "bilinear",

        ]

    ##################################################

    def summary(self):

        return {

            "algorithm": self.algorithm,

            "methods": self.available_methods(),

        }

    ##################################################

    def __repr__(self):

        return (

            f"InterpolationEngine("

            f"algorithm='{self.algorithm}')"

        )
