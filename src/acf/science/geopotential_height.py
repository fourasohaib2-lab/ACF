"""
Geopotential Height
===================

Conversion from geopotential to geopotential height.

Formula
-------
Z = Φ / g

where:
    Z : geopotential height (m)
    Φ : geopotential (m² s⁻²)
    g : gravity (m s⁻²)
"""

from acf.science.constants import G


class GeopotentialHeight:
    """Geopotential height calculator."""

    @staticmethod
    def calculate(geopotential: float) -> float:
        """
        Calculate geopotential height.

        Parameters
        ----------
        geopotential : float
            Geopotential (m² s⁻²)

        Returns
        -------
        float
            Geopotential height (m)
        """
        return geopotential / G
