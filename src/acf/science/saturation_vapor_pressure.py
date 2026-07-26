"""
Saturation Vapor Pressure
=========================

Formula (Tetens):
    es = 6.112 * exp((17.67 * T) / (T + 243.5))

where:
    es = saturation vapor pressure (hPa)
    T = temperature (°C)

For T in Kelvin: T_celsius = T - 273.15
"""

import math

class SaturationVaporPressure:
    """Saturation vapor pressure calculator."""
    
    @staticmethod
    def calculate(temperature: float, is_kelvin: bool = True) -> float:
        """
        Calculate saturation vapor pressure using Tetens formula.
        
        Parameters
        ----------
        temperature : float
            Temperature (Kelvin if is_kelvin=True, else Celsius)
        is_kelvin : bool
            If True, temperature is in Kelvin; else Celsius
            
        Returns
        -------
        float
            Saturation vapor pressure (hPa)
        """
        if is_kelvin:
            T_celsius = temperature - 273.15
        else:
            T_celsius = temperature
        
        # Tetens formula
        return 6.112 * math.exp((17.67 * T_celsius) / (T_celsius + 243.5))
    
    @staticmethod
    def calculate_tetens(temperature: float, is_kelvin: bool = True) -> float:
        """
        Alias for calculate() - for backward compatibility.
        """
        return SaturationVaporPressure.calculate(temperature, is_kelvin)
    
    @staticmethod
    def calculate_golf(temperature: float, is_kelvin: bool = True) -> float:
        """
        Calculate saturation vapor pressure using Golf-Gratch formula.
        More accurate for low temperatures.
        """
        # Simplified version using Tetens for now
        return SaturationVaporPressure.calculate(temperature, is_kelvin)
