"""
Atmospheric Complexity Framework (ACF)

Trilinear Interpolation
"""

from acf.model4d.interpolation.bilinear import BilinearInterpolation
from acf.model4d.interpolation.linear import LinearInterpolation


class TrilinearInterpolation:
    """
    Trilinear interpolation inside a cube.
    """

    @staticmethod
    def interpolate(
        c000,
        c100,
        c010,
        c110,
        c001,
        c101,
        c011,
        c111,
        tx,
        ty,
        tz,
    ):

        bottom = BilinearInterpolation.interpolate(
            c000,
            c100,
            c010,
            c110,
            tx,
            ty,
        )

        top = BilinearInterpolation.interpolate(
            c001,
            c101,
            c011,
            c111,
            tx,
            ty,
        )

        return LinearInterpolation.interpolate(
            0,
            bottom,
            1,
            top,
            tz,
        )
