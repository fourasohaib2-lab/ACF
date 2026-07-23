"""
Thermodynamics Engine
=====================
"""

from acf.science.temperature import Temperature
from acf.science.dewpoint import DewPoint
from acf.science.relative_humidity import RelativeHumidity
from acf.science.virtual_temperature import VirtualTemperature
from acf.science.potential_temperature import PotentialTemperature
from acf.science.equivalent_potential_temperature import (
    EquivalentPotentialTemperature,
)


class Thermodynamics:
    """
    Thermodynamics engine.
    """

    @staticmethod
    def available():

        return {
            "temperature": Temperature,
            "dewpoint": DewPoint,
            "relative_humidity": RelativeHumidity,
            "virtual_temperature": VirtualTemperature,
            "potential_temperature": PotentialTemperature,
            "equivalent_potential_temperature": (
                EquivalentPotentialTemperature
            ),
        }

