"""
ACF - Atmospheric Complexity Framework

Atmospheric Composition Transport Physics Module

Models simplified atmospheric transport of trace gases:
- CO2
- CH4
- O3
- NOx
- SO2

Includes:
- advection
- turbulent diffusion
- vertical mixing
- chemical transport
"""


class AtmosphericCompositionTransportPhysics:
    MODULE_NAME = "Atmospheric Composition Transport Physics"

    @staticmethod
    def advective_transport(concentration, wind_speed, gradient):
        """
        Horizontal atmospheric advection.

        Transport = wind speed × concentration gradient
        """

        if concentration < 0:
            raise ValueError("Concentration must be positive")

        if wind_speed < 0:
            raise ValueError("Wind speed must be positive")

        return wind_speed * gradient

    @staticmethod
    def turbulent_diffusion(diffusion_coefficient, gradient):
        """
        Turbulent mixing of atmospheric species.
        """

        if diffusion_coefficient < 0:
            raise ValueError("Diffusion coefficient must be positive")

        return diffusion_coefficient * gradient

    @staticmethod
    def vertical_mixing(concentration_difference, mixing_rate):
        """
        Vertical exchange between atmospheric layers.
        """

        if mixing_rate < 0:
            raise ValueError("Mixing rate must be positive")

        return concentration_difference * mixing_rate

    @staticmethod
    def chemical_lifetime_transport(concentration, lifetime):
        """
        Atmospheric chemical decay transport.

        remaining = concentration × lifetime factor
        """

        if concentration < 0:
            raise ValueError("Concentration must be positive")

        if lifetime < 0:
            raise ValueError("Lifetime must be positive")

        return concentration * lifetime

    @staticmethod
    def greenhouse_gas_loading(co2, ch4, ozone):
        """
        Simplified greenhouse gas atmospheric loading.
        """

        if co2 < 0 or ch4 < 0 or ozone < 0:
            raise ValueError("Gas concentrations must be positive")

        return co2 + ch4 + ozone

    @staticmethod
    def aerosol_gas_interaction(aerosol_mass, gas_concentration):
        """
        Coupling between aerosols and trace gases.
        """

        if aerosol_mass < 0:
            raise ValueError("Aerosol mass must be positive")

        if gas_concentration < 0:
            raise ValueError("Gas concentration must be positive")

        return aerosol_mass * gas_concentration

    @staticmethod
    def transport_status():

        return {
            "module": AtmosphericCompositionTransportPhysics.MODULE_NAME,
            "status": "active",
            "domain": "atmospheric composition transport",
        }
