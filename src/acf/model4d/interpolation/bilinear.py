"""
Atmospheric Complexity Framework (ACF)

Bilinear Interpolation
"""

from acf.model4d.interpolation.linear import LinearInterpolation


class BilinearInterpolation:
    """
    Bilinear interpolation on a rectangle.
    """

    @staticmethod
    def interpolate(
        q11,
        q21,
        q12,
        q22,
        tx,
        ty,
    ):
        """
        Bilinear interpolation.

        tx and ty must be between 0 and 1.
        """

        r1 = LinearInterpolation.interpolate(
            0,
            q11,
            1,
            q21,
            tx,
        )

        r2 = LinearInterpolation.interpolate(
            0,
            q12,
            1,
            q22,
            tx,
        )

        return LinearInterpolation.interpolate(
            0,
            r1,
            1,
            r2,
            ty,
        )
