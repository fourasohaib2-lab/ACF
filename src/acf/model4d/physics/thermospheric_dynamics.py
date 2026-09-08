"""
ACF - Atmospheric Complexity Framework
Thermospheric Dynamics Physics Module

Simulation simplifiée des processus thermosphériques :
- température thermosphérique
- densité atmosphérique
- expansion thermique
- chauffage solaire
- interaction ionosphère-thermosphère
- refroidissement radiatif
"""


class ThermosphericDynamicsPhysics:
    """
    Modèle physique simplifié de la thermosphère.
    """

    @staticmethod
    def solar_heating_flux(solar_input, absorption):
        """
        Chauffage solaire absorbé.

        Parameters:
            solar_input (float): énergie solaire incidente
            absorption (float): fraction absorbée

        Returns:
            float
        """
        return round(solar_input * absorption, 10)

    @staticmethod
    def thermospheric_temperature(base_temperature, heating):
        """
        Variation de température thermosphérique.
        """
        return base_temperature + heating

    @staticmethod
    def atmospheric_density(mass, volume):
        """
        Densité atmosphérique.
        """
        return mass / volume

    @staticmethod
    def thermal_expansion(coefficient, temperature_change):
        """
        Expansion thermique.
        """
        return coefficient * temperature_change

    @staticmethod
    def radiative_cooling(emission, coefficient):
        """
        Refroidissement radiatif.
        """
        return round(emission * coefficient, 10)

    @staticmethod
    def ionosphere_temperature_effect(electron_energy, factor):
        """
        Influence ionosphérique sur température.
        """
        return electron_energy * factor

    @staticmethod
    def thermosphere_pressure(density, temperature):
        """
        Pression simplifiée.
        """
        return density * temperature

    @staticmethod
    def molecular_diffusion(rate, time):
        """
        Diffusion moléculaire thermosphérique.
        """
        return rate * time

    @staticmethod
    def atmospheric_escape_velocity(temperature, factor):
        """
        Effet thermique sur échappement atmosphérique.
        """
        return temperature * factor

    @staticmethod
    def energy_balance(input_energy, lost_energy):
        """
        Bilan énergétique thermosphérique.
        """
        return input_energy - lost_energy
