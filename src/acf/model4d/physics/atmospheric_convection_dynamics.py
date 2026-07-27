"""
ACF - Atmospheric Complexity Framework
Model4D Physics Module

Atmospheric Convection Dynamics
Sprint 8.83

Processes:
- CAPE (Convective Available Potential Energy)
- CIN (Convective Inhibition)
- convective velocity
- heat transport
- vertical energy exchange
"""

from dataclasses import dataclass
import math


@dataclass
class ConvectionState:
    temperature_surface: float
    temperature_parcel: float
    environmental_temperature: float
    vertical_velocity: float
    heat_flux: float


class AtmosphericConvectionDynamics:
    """
    Atmospheric convection parameterization engine.
    """

    def __init__(self):
        self.name = "Atmospheric Convection Dynamics"
        self.version = "1.0"

    def calculate_buoyancy(
        self,
        parcel_temperature: float,
        environment_temperature: float
    ) -> float:
        """
        Simplified buoyancy proxy.
        Positive = rising air.
        """

        return (
            parcel_temperature - environment_temperature
        ) / environment_temperature


    def calculate_cape(
        self,
        buoyancy: float,
        height: float
    ) -> float:
        """
        CAPE approximation:
        CAPE = buoyancy * g * height
        """

        if height < 0:
            raise ValueError(
                "Height must be positive"
            )

        g = 9.81

        return max(
            0,
            buoyancy * g * height
        )


    def calculate_cin(
        self,
        negative_buoyancy: float,
        height: float
    ) -> float:
        """
        Convective inhibition.
        """

        if height < 0:
            raise ValueError(
                "Height must be positive"
            )

        return abs(
            min(
                0,
                negative_buoyancy
            )
        ) * 9.81 * height


    def convective_velocity(
        self,
        cape: float
    ) -> float:
        """
        Maximum convective updraft velocity.
        w = sqrt(2*CAPE)
        """

        if cape < 0:
            raise ValueError(
                "CAPE must be positive"
            )

        return math.sqrt(
            2 * cape
        )


    def heat_transport(
        self,
        heat_flux: float,
        area: float
    ) -> float:
        """
        Total transported heat.
        """

        if area <= 0:
            raise ValueError(
                "Area must be positive"
            )

        return heat_flux * area


    def analyze(
        self,
        state: ConvectionState,
        height: float
    ) -> dict:

        buoyancy = self.calculate_buoyancy(
            state.temperature_parcel,
            state.environmental_temperature
        )

        cape = self.calculate_cape(
            buoyancy,
            height
        )

        cin = self.calculate_cin(
            buoyancy,
            height
        )

        velocity = self.convective_velocity(
            cape
        )

        return {
            "module": self.name,
            "buoyancy": buoyancy,
            "cape": cape,
            "cin": cin,
            "updraft_velocity": velocity,
            "heat_flux": state.heat_flux
        }

