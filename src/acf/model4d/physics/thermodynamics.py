"""
ACF Model4D - Atmospheric Thermodynamics Module

Provides basic thermodynamic calculations
for atmospheric 4D fields.
"""


class Thermodynamics:
    """
    Thermodynamic operators for atmospheric modeling.
    """

    @staticmethod
    def temperature_conversion(celsius):
        """
        Convert Celsius to Kelvin.

        Parameters
        ----------
        celsius : float
            Temperature in Celsius.

        Returns
        -------
        float
            Temperature in Kelvin.
        """
        return celsius + 273.15

    @staticmethod
    def pressure_density(pressure, temperature, gas_constant=287.05):
        """
        Compute air density using ideal gas law.

        rho = P / (R * T)

        Parameters
        ----------
        pressure : float
            Pressure in Pa.

        temperature : float
            Temperature in Kelvin.

        gas_constant : float
            Specific gas constant for dry air.

        Returns
        -------
        float
            Air density kg/m3.
        """
        return pressure / (gas_constant * temperature)

    @staticmethod
    def potential_temperature(temperature, pressure,
                              reference_pressure=100000,
                              exponent=0.2854):
        """
        Compute potential temperature.

        theta = T * (P0/P)^k

        Parameters
        ----------
        temperature : float
            Temperature in Kelvin.

        pressure : float
            Pressure in Pa.

        Returns
        -------
        float
            Potential temperature.
        """
        return temperature * (
            reference_pressure / pressure
        ) ** exponent

    @staticmethod
    def heat_index(value):
        """
        Classify atmospheric thermal intensity.
        """
        if value < 250:
            return "Cold"

        if value < 280:
            return "Normal"

        if value < 310:
            return "Warm"

        return "Hot"
