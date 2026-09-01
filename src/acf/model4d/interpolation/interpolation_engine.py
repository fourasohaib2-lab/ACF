"""
Atmospheric Complexity Framework (ACF)

Interpolation Engine
====================

NOTE (correction): nearest()/linear()/bilinear() below used to just
deepcopy(values) and return it unchanged - three differently-named
"interpolation methods" that were actually identical no-ops, silently
returning the input untouched regardless of which method was
requested. This class's own API is missing the target coordinate(s)
a real interpolation would need (values alone, with no query point, is
not enough to interpolate to anywhere) - so genuine nearest/linear/
bilinear interpolation cannot be performed with this signature as
designed. Not fabricated data (no specific numeric claim is made,
values are genuinely echoed), but still misleading: the class/method
names claim three distinct numerical techniques that the actual
computation cannot and does not perform. For real interpolation, use
LinearInterpolation/BilinearInterpolation/TrilinearInterpolation/
VerticalInterpolation/TemporalInterpolation in this same package,
which do take genuine target coordinates and are independently
verified correct.
"""

from copy import deepcopy


class InterpolationEngine:
    """
    NOTE: this engine's methods are pass-through placeholders, not real
    interpolation - see module NOTE above for why and for the real
    implementations to use instead.
    """

    def __init__(self):

        self.algorithm = "nearest"

    ##################################################

    def nearest(self, values):
        """Placeholder - returns values unchanged (no target coordinate in this API to interpolate to)."""

        return deepcopy(values)

    ##################################################

    def linear(self, values):
        """Placeholder - returns values unchanged (no target coordinate in this API to interpolate to)."""

        return deepcopy(values)

    ##################################################

    def bilinear(self, values):
        """Placeholder - returns values unchanged (no target coordinate in this API to interpolate to)."""

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

        return f"InterpolationEngine(algorithm='{self.algorithm}')"
