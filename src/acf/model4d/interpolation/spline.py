"""
Atmospheric Complexity Framework (ACF)

Spline Interpolation
"""


class SplineInterpolation:
    """
    Natural cubic spline interpolation.
    Lightweight implementation used by the ACF 4D engine.
    """

    @staticmethod
    def interpolate(y0, y1, y2, y3, t):
        """
        Cubic spline interpolation.

        Parameters
        ----------
        y0, y1, y2, y3 : float
            Neighboring values.

        t : float
            Position in [0,1].
        """

        a = (-y0 + 3*y1 - 3*y2 + y3) / 6.0
        b = (y0 - 2*y1 + y2) / 2.0
        c = (-y0 + y2) / 2.0
        d = (y0 + 4*y1 + y2) / 6.0

        return (
            ((a * t + b) * t + c) * t + d
        )

    @staticmethod
    def midpoint(y0, y1, y2, y3):
        """
        Value at t = 0.5
        """

        return SplineInterpolation.interpolate(
            y0,
            y1,
            y2,
            y3,
            0.5,
        )

    @staticmethod
    def endpoints(y1, y2):
        """
        Return interpolation endpoints.
        """

        return (y1, y2)
