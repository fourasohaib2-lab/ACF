"""
ACF - Atmospheric Complexity Framework
Climate Sensitivity Parameter Physics Module

Sprint 9.03
"""

from dataclasses import dataclass


@dataclass
class ClimateSensitivityState:
    """
    State variables for climate sensitivity calculation.
    """

    forcing_wm2: float
    feedback_parameter: float
    equilibrium_factor: float = 1.0


class ClimateSensitivityParameter:
    """
    Computes simplified planetary climate sensitivity.

    Represents:
        temperature response = forcing × feedback × equilibrium factor
    """

    def calculate_sensitivity(self, state: ClimateSensitivityState) -> float:
        """
        Calculate climate sensitivity response.
        """

        return state.forcing_wm2 * state.feedback_parameter * state.equilibrium_factor

    def temperature_response(self, forcing: float, sensitivity: float) -> float:
        """
        Estimate temperature anomaly.
        """

        return forcing * sensitivity
