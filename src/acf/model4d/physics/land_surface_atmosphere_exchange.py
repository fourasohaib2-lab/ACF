"""
Atmospheric Complexity Framework (ACF)

MODEL4D - Land Surface Atmosphere Exchange

Purpose:
--------
4D spatio-temporal grid mechanics, field representations, differential operators, and physical parameterizations.

Responsibilities:
-----------------
• Manage land surface atmosphere exchange logic and state representations.
• Integrate with the model4d subsystem of the ACF scientific engine.

Major Components:
-----------------
• SurfaceExchangeState, LandSurfaceAtmosphereExchange

Dependencies:
-------------
• Python Standard Library and NumPy/Scientific Python Stack.
• Internal acf.model4d module infrastructure.

Scientific Context:
-------------------
Provides foundational capabilities for numerical weather prediction, atmospheric data processing,
physical modeling, and spatial-temporal analysis within the Atmospheric Complexity Framework.
"""

from dataclasses import dataclass


@dataclass
class SurfaceExchangeState:
    net_radiation: float
    soil_temperature: float
    air_temperature: float
    soil_moisture: float
    vegetation_fraction: float
    albedo: float


class LandSurfaceAtmosphereExchange:
    """
    Land surface - atmosphere interaction model.

    Simplified physical parameterization for ACF Model 4D.
    """

    def surface_energy_balance(self, state: SurfaceExchangeState) -> float:
        """
        Compute surface energy balance.
        """
        return round(state.net_radiation * (1 - state.albedo) * state.vegetation_fraction, 2)

    def soil_heat_flux(self, state: SurfaceExchangeState) -> float:
        """
        Soil conductive heat exchange.
        """
        return round((state.soil_temperature - state.air_temperature) * state.soil_moisture, 2)

    def evapotranspiration(self, state: SurfaceExchangeState) -> float:
        """
        Estimate evapotranspiration flux.
        """
        return round(state.soil_moisture * state.vegetation_fraction * 10, 2)

    def surface_albedo_effect(self, state: SurfaceExchangeState) -> float:
        """
        Radiative cooling/heating effect from albedo.
        """
        return round(state.net_radiation * state.albedo, 2)

    def soil_moisture_feedback(self, state: SurfaceExchangeState) -> float:
        """
        Soil moisture feedback on atmosphere.
        """
        return round(state.soil_moisture * (1 - state.albedo), 2)

    def radiative_exchange(self, state: SurfaceExchangeState) -> float:
        """
        Simplified radiative exchange.
        """
        return round(state.net_radiation * (1 - state.albedo), 2)
