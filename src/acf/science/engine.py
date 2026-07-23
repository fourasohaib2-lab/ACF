"""
Science Engine
==============

Main scientific engine of ACF.
"""

from acf.science.thermodynamics import Thermodynamics
from acf.science.dynamics import Dynamics
from acf.science.severe_weather import SevereWeather


class ScienceEngine:
    """Main scientific engine."""

    def __init__(self):
        self.thermodynamics = Thermodynamics()
        self.dynamics = Dynamics()
        self.severe_weather = SevereWeather()

    def available(self):
        """Return available scientific engines."""

        return {
            "thermodynamics": self.thermodynamics,
            "dynamics": self.dynamics,
            "severe_weather": self.severe_weather,
        }
