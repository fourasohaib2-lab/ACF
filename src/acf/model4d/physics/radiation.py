"""
ACF - Atmospheric Complexity Framework
Model4D Physics - Radiation Module

Handles simplified atmospheric radiation calculations:
- Stefan-Boltzmann radiation
- Net radiation balance
- Shortwave / Longwave components
- Radiative categories
"""


class Radiation:
    """
    Radiation physics operator for atmospheric models.
    """

    STEFAN_BOLTZMANN = 5.670374419e-8

    @staticmethod
    def stefan_boltzmann(
        temperature: float,
        emissivity: float = 1.0
    ) -> float:
        """
        Calculate emitted radiation flux.

        Formula:
        F = ε σ T⁴

        Parameters:
            temperature: Kelvin
            emissivity: 0-1

        Returns:
            W/m²
        """
        return emissivity * Radiation.STEFAN_BOLTZMANN * temperature ** 4


    @staticmethod
    def net_balance(
        incoming: float,
        outgoing: float
    ) -> float:
        """
        Net radiation balance.

        Positive = warming
        Negative = cooling
        """
        return incoming - outgoing


    @staticmethod
    def shortwave(
        solar: float,
        albedo: float
    ) -> float:
        """
        Absorbed shortwave radiation.

        SW = Solar * (1 - albedo)
        """
        return solar * (1 - albedo)


    @staticmethod
    def longwave(
        surface_temperature: float
    ) -> float:
        """
        Surface longwave emission.
        """
        return Radiation.stefan_boltzmann(surface_temperature)


    @staticmethod
    def category(value: float) -> str:
        """
        Radiation intensity classification.
        """

        if value < 50:
            return "Weak"

        if value < 300:
            return "Moderate"

        return "Strong"
