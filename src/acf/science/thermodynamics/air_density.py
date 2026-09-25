"""
Air Density
===========

Calculation of dry air density using the ideal gas law.

Formula
-------
rho = p / (Rd * T)
"""

RD = 287.05


class AirDensity:
    """Air density calculator."""

    @staticmethod
    def calculate(
        pressure_pa: float,
        temperature_k: float,
    ) -> float:
        """
        Calculate air density.

        Parameters
        ----------
        pressure_pa : float
            Atmospheric pressure (Pa)

        temperature_k : float
            Air temperature (K)

        Returns
        -------
        float
            Air density (kg/m³)
        """
        if pressure_pa <= 0:
            raise ValueError("pressure must be positive.")

        if temperature_k <= 0:
            raise ValueError("temperature must be positive.")

        return pressure_pa / (RD * temperature_k)
