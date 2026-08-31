"""
ACF Model4D - Operators Engine

Centralisation des opérateurs physiques :
- Gradient
- Divergence
- Laplacian
- Curl
- Advection
- Diffusion
"""

from .advection import Advection
from .curl import Curl
from .diffusion import Diffusion
from .divergence import Divergence
from .gradient import Gradient
from .laplacian import Laplacian


class OperatorsEngine:
    """
    Moteur central des opérateurs Model4D.
    """

    def gradient(self, *args, **kwargs):
        return Gradient.calculate(*args, **kwargs)

    def divergence(self, *args, **kwargs):
        return Divergence.compute(*args, **kwargs)

    def laplacian(self, *args, **kwargs):
        return Laplacian.calculate(*args, **kwargs)

    def curl(self, *args, **kwargs):
        return Curl.compute(*args, **kwargs)

    def advection(self, *args, **kwargs):
        return Advection.compute(*args, **kwargs)

    def diffusion(self, *args, **kwargs):
        return Diffusion.calculate(*args, **kwargs)

    def apply(self, operator, *args, **kwargs):
        """
        Application dynamique d'un opérateur.
        """

        operators = {
            "gradient": self.gradient,
            "divergence": self.divergence,
            "laplacian": self.laplacian,
            "curl": self.curl,
            "advection": self.advection,
            "diffusion": self.diffusion,
        }

        if operator not in operators:
            raise ValueError(f"Unknown operator: {operator}")

        return operators[operator](*args, **kwargs)
