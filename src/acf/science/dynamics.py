"""
Dynamics Engine
===============

Groups all atmospheric dynamics diagnostics.
"""

from acf.science.divergence import Divergence
from acf.science.frontogenesis import Frontogenesis
from acf.science.geopotential_height import GeopotentialHeight
from acf.science.hypsometric_equation import HypsometricEquation
from acf.science.potential_vorticity import PotentialVorticity
from acf.science.vorticity import Vorticity


class Dynamics:
    """Atmospheric dynamics engine."""

    @staticmethod
    def available():
        return {
            "vorticity": Vorticity,
            "divergence": Divergence,
            "frontogenesis": Frontogenesis,
            "potential_vorticity": PotentialVorticity,
            "geopotential_height": GeopotentialHeight,
            "hypsometric_equation": HypsometricEquation,
        }
