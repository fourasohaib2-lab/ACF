"""
Dynamics Engine
===============

Groups all atmospheric dynamics diagnostics.
"""

from acf.science.dynamics.divergence import Divergence
from acf.science.dynamics.frontogenesis import Frontogenesis
from acf.science.dynamics.potential_vorticity import PotentialVorticity
from acf.science.dynamics.vorticity import Vorticity
from acf.science.thermodynamics.geopotential_height import GeopotentialHeight
from acf.science.thermodynamics.hypsometric_equation import HypsometricEquation


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
