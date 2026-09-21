"""
Thermodynamics Module
=====================

Combines all thermodynamic calculations for ACF.
"""

from .dry_static_energy import DryStaticEnergy
from .equivalent_potential_temperature import EquivalentPotentialTemperature
from .hypsometric_equation import HypsometricEquation
from .mixing_ratio import MixingRatio
from .moist_static_energy import MoistStaticEnergy
from .potential_temperature import PotentialTemperature
from .saturation_mixing_ratio import SaturationMixingRatio
from .saturation_vapor_pressure import SaturationVaporPressure
from .vapor_pressure import VaporPressure
from .virtual_temperature import VirtualTemperature
from .wet_bulb_temperature import WetBulbTemperature


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
    def calculate_saturation_mixing_ratio(saturation_vapor_pressure: float, pressure: float) -> float:
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
    def calculate_saturation_vapor_pressure(temperature: float, is_kelvin: bool = True) -> float:
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
        specific_humidity: float, pressure: float, temperature: float, is_kelvin: bool = True
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

    @staticmethod
    def calculate_potential_temperature(temperature_k: float, pressure_hpa: float) -> float:
        """
        Calculate potential temperature theta = T * (p0/p)^(Rd/Cp).

        Parameters
        ----------
        temperature_k : float
            Temperature in Kelvin
        pressure_hpa : float
            Pressure in hPa

        Returns
        -------
        float
            Potential temperature in Kelvin
        """
        return PotentialTemperature.calculate(temperature_k, pressure_hpa)

    @staticmethod
    def calculate_equivalent_potential_temperature(
        temperature_k: float, specific_humidity: float
    ) -> float:
        """
        Calculate equivalent potential temperature (simple approximation).

        See EquivalentPotentialTemperature.calculate_bolton_1980() for the
        canonical, referenced formula (needs dewpoint and pressure).

        Parameters
        ----------
        temperature_k : float
            Temperature in Kelvin
        specific_humidity : float
            Specific humidity in kg/kg

        Returns
        -------
        float
            Equivalent potential temperature in Kelvin
        """
        return EquivalentPotentialTemperature.calculate(temperature_k, specific_humidity)

    @staticmethod
    def calculate_equivalent_potential_temperature_bolton(
        temperature_k: float, dewpoint_k: float, pressure_hpa: float
    ) -> float:
        """
        Calculate equivalent potential temperature (canonical, Bolton 1980).

        Parameters
        ----------
        temperature_k : float
            Air temperature in Kelvin
        dewpoint_k : float
            Dewpoint temperature in Kelvin
        pressure_hpa : float
            Atmospheric pressure in hPa

        Returns
        -------
        float
            Equivalent potential temperature in Kelvin

        References
        ----------
        Bolton, D. (1980). Mon. Wea. Rev., 108(7), 1046-1053.
        """
        return EquivalentPotentialTemperature.calculate_bolton_1980(temperature_k, dewpoint_k, pressure_hpa)

    @staticmethod
    def calculate_wet_bulb_temperature(temperature_c: float, relative_humidity: float) -> float:
        """
        Calculate wet bulb temperature (Stull 2011 approximation).

        Parameters
        ----------
        temperature_c : float
            Air temperature in Celsius
        relative_humidity : float
            Relative humidity in [0, 1]

        Returns
        -------
        float
            Wet bulb temperature in Celsius
        """
        return WetBulbTemperature.calculate(temperature_c, relative_humidity)

    @staticmethod
    def calculate_dry_static_energy(temperature_k: float, height_m: float) -> float:
        """
        Calculate dry static energy s = Cp*T + g*z.

        Parameters
        ----------
        temperature_k : float
            Temperature in Kelvin
        height_m : float
            Geopotential height in meters

        Returns
        -------
        float
            Dry static energy in J/kg
        """
        return DryStaticEnergy.calculate(temperature_k, height_m)

    @staticmethod
    def calculate_moist_static_energy(
        temperature_k: float, height_m: float, specific_humidity: float
    ) -> float:
        """
        Calculate moist static energy h = Cp*T + g*z + Lv*q.

        Parameters
        ----------
        temperature_k : float
            Temperature in Kelvin
        height_m : float
            Geopotential height in meters
        specific_humidity : float
            Specific humidity in kg/kg

        Returns
        -------
        float
            Moist static energy in J/kg
        """
        return MoistStaticEnergy.calculate(temperature_k, height_m, specific_humidity)

    @staticmethod
    def calculate_hypsometric_thickness(
        pressure1_pa: float, pressure2_pa: float, virtual_temperature_k: float
    ) -> float:
        """
        Calculate layer thickness via the hypsometric equation.

        Parameters
        ----------
        pressure1_pa : float
            Lower-level pressure in Pa
        pressure2_pa : float
            Upper-level pressure in Pa
        virtual_temperature_k : float
            Mean virtual temperature of the layer in Kelvin

        Returns
        -------
        float
            Layer thickness in meters
        """
        return HypsometricEquation.calculate(pressure1_pa, pressure2_pa, virtual_temperature_k)
