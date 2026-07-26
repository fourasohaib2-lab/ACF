"""
ACF - Atmospheric Complexity Framework
Model4D Physics - Precipitation Module

Handles simplified atmospheric precipitation processes.
"""

from dataclasses import dataclass


@dataclass
class Precipitation:
    """
    Basic precipitation physics representation.

    Parameters
    ----------
    rain_rate : float
        Rainfall rate (mm/h)
    cloud_water : float
        Cloud water content (kg/m3)
    temperature : float
        Air temperature (K)
    """

    rain_rate: float = 0.0
    cloud_water: float = 0.0
    temperature: float = 288.0

    def condensation_rate(self) -> float:
        """
        Estimate condensation contribution.

        Returns
        -------
        float
            Condensation rate.
        """
        return max(self.cloud_water * 0.1, 0.0)

    def precipitation_efficiency(self) -> float:
        """
        Compute precipitation efficiency.

        Returns
        -------
        float
            Efficiency between 0 and 1.
        """
        if self.cloud_water <= 0:
            return 0.0

        efficiency = self.rain_rate / (self.cloud_water * 1000)

        return min(max(efficiency, 0.0), 1.0)

    def evaporation_loss(self) -> float:
        """
        Estimate evaporation loss.

        Returns
        -------
        float
            Evaporation amount.
        """
        if self.temperature > 273.15:
            return self.rain_rate * 0.05

        return 0.0

    def update(self, timestep: float = 1.0) -> float:
        """
        Update precipitation state.

        Parameters
        ----------
        timestep : float
            Simulation time step.

        Returns
        -------
        float
            Updated rainfall rate.
        """

        condensation = self.condensation_rate()

        evaporation = self.evaporation_loss()

        self.rain_rate += (condensation - evaporation) * timestep

        self.rain_rate = max(self.rain_rate, 0.0)

        return self.rain_rate

