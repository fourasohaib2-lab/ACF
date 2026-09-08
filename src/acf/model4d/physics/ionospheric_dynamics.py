"""
ACF - Atmospheric Complexity Framework
Ionospheric Dynamics Physics Module

Sprint 8.72

Handles simplified ionosphere physical interactions:
- electron density
- ionization rate
- plasma frequency
- solar radiation influence
- ionospheric temperature
- recombination processes
- TEC (Total Electron Content)
"""


class IonosphericDynamicsPhysics:
    """
    Simplified ionospheric physics engine.
    """

    @staticmethod
    def ionization_rate(solar_flux, neutral_density):
        """
        Ionization production rate.

        Formula:
        rate = solar_flux / neutral_density
        """
        if neutral_density <= 0:
            raise ValueError("neutral_density must be positive")

        return solar_flux / neutral_density

    @staticmethod
    def electron_density(ionization, recombination):
        """
        Electron density variation.

        Formula:
        Ne = ionization - recombination
        """
        return ionization - recombination

    @staticmethod
    def recombination_rate(electron_density, coefficient):
        """
        Plasma recombination.

        Formula:
        R = Ne * coefficient
        """
        return electron_density * coefficient

    @staticmethod
    def plasma_frequency(electron_density):
        """
        Simplified plasma frequency.

        Formula:
        fp = sqrt(Ne)
        """
        if electron_density < 0:
            raise ValueError("electron_density cannot be negative")

        return round(electron_density**0.5, 6)

    @staticmethod
    def solar_ionization_effect(solar_flux, efficiency):
        """
        Solar energy converted into ionization.

        Formula:
        effect = solar_flux * efficiency
        """
        return round(solar_flux * efficiency, 6)

    @staticmethod
    def ionospheric_temperature(base_temperature, heating):
        """
        Temperature increase.

        Formula:
        T = base + heating
        """
        return base_temperature + heating

    @staticmethod
    def electron_temperature_change(initial_temperature, energy_input):
        """
        Electron temperature response.
        """
        return initial_temperature + energy_input

    @staticmethod
    def total_electron_content(electron_density, altitude):
        """
        TEC simplified estimation.

        Formula:
        TEC = Ne * altitude
        """
        return electron_density * altitude

    @staticmethod
    def ionosphere_stability(index):
        """
        Stability indicator.
        """
        if index < 0:
            return "unstable"

        if index > 1:
            return "high"

        return "normal"

    @staticmethod
    def geomagnetic_disturbance_effect(storm_index):
        """
        Geomagnetic storm influence.
        """
        return round(storm_index * 10, 6)
