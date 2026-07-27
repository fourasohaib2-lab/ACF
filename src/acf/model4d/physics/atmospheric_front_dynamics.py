"""
ACF - Atmospheric Complexity Framework
Model 4D Physics Engine

Module:
Atmospheric Front Dynamics

Description:
Simulation and diagnostics of atmospheric fronts:
- cold fronts
- warm fronts
- occluded fronts
- stationary fronts
- thermal gradients
- frontal lifting
- pressure interactions
- precipitation potential

Sprint:
8.87
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class FrontState:
    temperature_gradient: float
    pressure_gradient: float
    humidity_gradient: float
    wind_speed: float
    lifting_rate: float


class AtmosphericFrontDynamics:
    """
    Atmospheric frontal dynamics model.

    Inputs:
        temperature gradient (K/km)
        pressure gradient (hPa/km)
        humidity gradient
        wind speed (m/s)
        lifting rate (m/s)

    Outputs:
        front intensity
        stability index
        precipitation potential
    """

    MODULE_NAME = "Atmospheric Front Dynamics"

    def __init__(self):
        self.version = "8.87"

    def calculate_front_intensity(
        self,
        temperature_gradient: float,
        pressure_gradient: float,
        humidity_gradient: float,
        wind_speed: float,
    ) -> float:

        intensity = (
            abs(temperature_gradient) * 0.4
            + abs(pressure_gradient) * 0.3
            + abs(humidity_gradient) * 0.2
            + wind_speed * 0.1
        )

        return round(intensity, 3)

    def calculate_lifting_energy(
        self,
        lifting_rate: float,
        temperature_gradient: float,
    ) -> float:

        energy = lifting_rate * (1 + abs(temperature_gradient))

        return round(energy, 3)

    def precipitation_probability(
        self,
        humidity_gradient: float,
        lifting_rate: float,
    ) -> float:

        probability = (
            abs(humidity_gradient) * 40
            + lifting_rate * 60
        )

        return min(round(probability, 2), 100.0)

    def classify_front(
        self,
        temperature_gradient: float,
        wind_speed: float,
    ) -> str:

        if temperature_gradient > 2 and wind_speed > 10:
            return "cold_front"

        if temperature_gradient < -2 and wind_speed < 10:
            return "warm_front"

        if abs(temperature_gradient) < 0.5:
            return "stationary_front"

        return "occluded_front"

    def diagnose(
        self,
        state: FrontState,
    ) -> Dict:

        intensity = self.calculate_front_intensity(
            state.temperature_gradient,
            state.pressure_gradient,
            state.humidity_gradient,
            state.wind_speed,
        )

        lifting = self.calculate_lifting_energy(
            state.lifting_rate,
            state.temperature_gradient,
        )

        precipitation = self.precipitation_probability(
            state.humidity_gradient,
            state.lifting_rate,
        )

        front_type = self.classify_front(
            state.temperature_gradient,
            state.wind_speed,
        )

        return {
            "module": self.MODULE_NAME,
            "version": self.version,
            "front_type": front_type,
            "intensity": intensity,
            "lifting_energy": lifting,
            "precipitation_probability": precipitation,
        }
