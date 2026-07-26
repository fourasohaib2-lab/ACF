"""
Atmospheric Complexity Framework (ACF)

Cubic Interpolation
"""


class CubicInterpolation:
    """
    Cubic interpolation using the Catmull-Rom spline.
    """

    @staticmethod
    def interpolate(p0, p1, p2, p3, t):
        """
        Interpolate between p1 and p2.

        Parameters
        ----------
        p0, p1, p2, p3 : float
            Four neighboring points.

        t : float
            Position between p1 and p2 (0 <= t <= 1).
        """

        a = (
            -0.5 * p0
            + 1.5 * p1
            - 1.5 * p2
            + 0.5 * p3
        )

        b = (
            p0
            - 2.5 * p1
            + 2.0 * p2
            - 0.5 * p3
        )

        c = (
            -0.5 * p0
            + 0.5 * p2
        )

        d = p1

        return (
            a * t**3
            + b * t**2
            + c * t
            + d
        )
