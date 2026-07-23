"""
Specific Humidity
=================

Calculation of specific humidity from mixing ratio.

Formula
-------
q = w / (1 + w)

where:
    q : specific humidity (kg/kg)
    w : mixing ratio (kg/kg)
"""


class SpecificHumidity:
    """Specific humidity calculator."""

    @staticmethod
    def calculate(mixing_ratio: float) -> float:
        """
        Calculate specific humidity.

        Parameters
        ----------
        mixing_ratio : float
            Mixing ratio (kg/kg)

        Returns
        -------
        float
            Specific humidity (kg/kg)
        """
        return mixing_ratio / (1.0 + mixing_ratio)
