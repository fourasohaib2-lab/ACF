"""
Atmospheric Complexity Framework (ACF)

Spline Interpolation
"""


class SplineInterpolation:
    """
    Uniform cubic B-spline (not a natural cubic spline - see NOTE below).
    Lightweight implementation used by the ACF 4D engine.

    NOTE (correction): this class and its docstrings used to call
    itself "Natural cubic spline interpolation" - a natural cubic
    spline, by definition, is an INTERPOLATING spline: it passes
    exactly through every given data point (solving a global
    tridiagonal system with a "natural"/zero-second-derivative
    boundary condition). The formula actually implemented here is the
    standard uniform cubic B-spline basis function evaluated locally
    from 4 neighboring control points - a smoothing/APPROXIMATING
    spline that does NOT pass through its control points in general
    (e.g. interpolate(0, 10, 0, 0, t=0) returns (0+40+0)/6 ≈ 6.67, not
    10). The math itself is a correct, standard, useful technique
    (this is exactly the right formula for a uniform cubic B-spline) -
    only the name/documentation was wrong. endpoints() likewise
    returns the two central control points bounding this segment, not
    the curve's actual value at t=0/t=1 (which do not equal y1/y2).
    """

    @staticmethod
    def interpolate(y0, y1, y2, y3, t):
        """
        Uniform cubic B-spline basis evaluation (does not pass through y1/y2 exactly - see class NOTE).

        Parameters
        ----------
        y0, y1, y2, y3 : float
            Four neighboring control points.

        t : float
            Position in [0,1] along the segment governed by y1, y2 (and influenced by y0, y3).
        """

        a = (-y0 + 3 * y1 - 3 * y2 + y3) / 6.0
        b = (y0 - 2 * y1 + y2) / 2.0
        c = (-y0 + y2) / 2.0
        d = (y0 + 4 * y1 + y2) / 6.0

        return ((a * t + b) * t + c) * t + d

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
        Return the segment's two central control points (y1, y2) - NOT the curve's
        actual value at t=0/t=1, which generally differ for a B-spline (see class NOTE).
        """

        return (y1, y2)
