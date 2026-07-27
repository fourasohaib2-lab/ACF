"""
ACF - Atmospheric Complexity Framework

Atmospheric Carbon Cycle Dynamics Physics Module

Sprint 9.06
"""

from dataclasses import dataclass


@dataclass
class CarbonCycleState:
    """
    Carbon reservoirs and fluxes.
    """

    emissions: float
    ocean_uptake: float
    vegetation_uptake: float
    soil_storage: float = 0.0


class AtmosphericCarbonCycleDynamics:
    """
    Simplified atmospheric carbon cycle model.

    Net atmospheric carbon change:

        emissions - natural sinks
    """

    def natural_sink(
        self,
        state: CarbonCycleState
    ) -> float:
        """
        Calculate total carbon absorption.
        """

        return (
            state.ocean_uptake
            + state.vegetation_uptake
            + state.soil_storage
        )


    def atmospheric_carbon_change(
        self,
        state: CarbonCycleState
    ) -> float:
        """
        Calculate atmospheric CO2 variation.
        """

        return (
            state.emissions
            - self.natural_sink(state)
        )


    def carbon_state(
        self,
        state: CarbonCycleState
    ) -> str:
        """
        Determine atmospheric carbon tendency.
        """

        change = self.atmospheric_carbon_change(state)

        if change > 0:
            return "increasing"

        if change < 0:
            return "decreasing"

        return "stable"
