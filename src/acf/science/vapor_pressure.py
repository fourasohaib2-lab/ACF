"""
Vapor Pressure
==============

Formula:
    e = q * p / (epsilon + q * (1 - epsilon))

where:
    e = vapor pressure (hPa)
    q = specific humidity (kg/kg)
    p = atmospheric pressure (hPa)
    epsilon = 0.622 (molecular weight ratio)
"""


class VaporPressure:
    """Vapor pressure calculator."""

    EPSILON = 0.622

    @staticmethod
    def calculate(specific_humidity: float, pressure: float) -> float:
        """
        Calculate vapor pressure.

        Parameters
        ----------
        specific_humidity : float
            Specific humidity (kg/kg) in [0, 1]
        pressure : float
            Atmospheric pressure (hPa)

        Returns
        -------
        float
            Vapor pressure (hPa)
        """
        if specific_humidity < 0.0 or specific_humidity > 1.0:
            raise ValueError("Specific humidity must be in [0, 1]")
        if pressure <= 0:
            raise ValueError("Pressure must be positive")

        epsilon = VaporPressure.EPSILON
        denominator = epsilon + specific_humidity * (1.0 - epsilon)

        # Éviter division par zéro
        if denominator == 0:
            return 0.0

        return specific_humidity * pressure / denominator
