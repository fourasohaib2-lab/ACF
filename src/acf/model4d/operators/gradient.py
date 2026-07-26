"""
Atmospheric Complexity Framework (ACF)

Gradient Operator
"""


class Gradient:
    """
    Numerical gradient operator.
    """

    @staticmethod
    def forward(left, right, spacing=1.0):
        """
        Forward difference.
        """
        return (right - left) / spacing

    @staticmethod
    def backward(left, right, spacing=1.0):
        """
        Backward difference.
        """
        return (right - left) / spacing

    @staticmethod
    def centered(left, right, spacing=1.0):
        """
        Centered difference.
        """
        return (right - left) / (2.0 * spacing)

    @staticmethod
    def magnitude(gx, gy=0.0, gz=0.0):
        """
        Gradient magnitude.
        """
        return (gx**2 + gy**2 + gz**2) ** 0.5
