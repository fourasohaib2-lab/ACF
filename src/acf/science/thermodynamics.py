"""
Thermodynamics Module
=====================

Combines all thermodynamic calculations for ACF.
"""

from .virtual_temperature import VirtualTemperature
from .specific_humidity import SpecificHumidity
from .mixing_ratio import MixingRatio
from .saturation_mixing_ratio import SaturationMixingRatio
from .vapor_pressure import VaporPressure
from .saturation_vapor_pressure import SaturationVaporPressure


class Thermodynamics:
    """
    Complete thermodynamic calculator for ACF.
    
    Provides methods for calculating atmospheric thermodynamic
    parameters from standard variables.
    """
    
    @staticmethod
    def calculate_virtual_temperature(temperature: float, specific_humidity: float) -> float:
        """
        Calculate virtual temperature.
        
        Parameters
        ----------
        temperature : float
            Air temperature in Kelvin
        specific_humidity : float
            Specific humidity in kg/kg
            
        Returns
        -------
        float
            Virtual temperature in Kelvin
        """
        return VirtualTemperature.calculate(temperature, specific_humidity)
    
    @staticmethod
    def calculate_mixing_ratio(specific_humidity: float) -> float:
        """
        Calculate mixing ratio.
        
        Parameters
        ----------
        specific_humidity : float
            Specific humidity in kg/kg
            
        Returns
        -------
        float
            Mixing ratio in kg/kg
        """
        return MixingRatio.calculate(specific_humidity)
    
    @staticmethod
    def calculate_saturation_mixing_ratio(
        saturation_vapor_pressure: float,
        pressure: float
    ) -> float:
        """
        Calculate saturation mixing ratio.
        
        Parameters
        ----------
        saturation_vapor_pressure : float
            Saturation vapor pressure in hPa
        pressure : float
            Atmospheric pressure in hPa
            
        Returns
        -------
        float
            Saturation mixing ratio in kg/kg
        """
        return SaturationMixingRatio.calculate(saturation_vapor_pressure, pressure)
    
    @staticmethod
    def calculate_vapor_pressure(specific_humidity: float, pressure: float) -> float:
        """
        Calculate vapor pressure.
        
        Parameters
        ----------
        specific_humidity : float
            Specific humidity in kg/kg
        pressure : float
            Atmospheric pressure in hPa
            
        Returns
        -------
        float
            Vapor pressure in hPa
        """
        return VaporPressure.calculate(specific_humidity, pressure)
    
    @staticmethod
    def calculate_saturation_vapor_pressure(
        temperature: float,
        is_kelvin: bool = True
    ) -> float:
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
            Saturation vapor pressure in hPa
        """
        return SaturationVaporPressure.calculate(temperature, is_kelvin)
    
    @staticmethod
    def calculate_relative_humidity(
        specific_humidity: float,
        pressure: float,
        temperature: float,
        is_kelvin: bool = True
    ) -> float:
        """
        Calculate relative humidity.
        
        Parameters
        ----------
        specific_humidity : float
            Specific humidity in kg/kg
        pressure : float
            Atmospheric pressure in hPa
        temperature : float
            Temperature (Kelvin if is_kelvin=True, else Celsius)
        is_kelvin : bool
            If True, temperature is in Kelvin; else Celsius
            
        Returns
        -------
        float
            Relative humidity in percent
        """
        e = VaporPressure.calculate(specific_humidity, pressure)
        es = SaturationVaporPressure.calculate(temperature, is_kelvin)
        
        if es == 0:
            return 0.0
        
        return min(100.0, (e / es) * 100.0)
