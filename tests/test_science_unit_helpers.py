"""
Atmospheric Complexity Framework (ACF)

SCIENCE - basic unit-conversion helper test suite
(Humidity.clip, Pressure.pa_to_hpa/hpa_to_pa, Temperature.kelvin_to_celsius/
celsius_to_kelvin, Wind.speed)

These 4 modules previously had 0% coverage - no test file imported
them at all. Trivial, exact conversions, but closing the gap for
completeness.
"""

import math

from acf.science.humidity import Humidity
from acf.science.pressure import Pressure
from acf.science.temperature import Temperature
from acf.science.wind import Wind


def test_humidity_clip():
    assert Humidity.clip(50.0) == 50.0
    assert Humidity.clip(-10.0) == 0.0
    assert Humidity.clip(150.0) == 100.0


def test_pressure_conversions_are_inverses():
    assert Pressure.pa_to_hpa(101325.0) == 1013.25
    assert Pressure.hpa_to_pa(1013.25) == 101325.0
    assert Pressure.hpa_to_pa(Pressure.pa_to_hpa(50000.0)) == 50000.0


def test_temperature_conversions_are_inverses():
    assert Temperature.kelvin_to_celsius(273.15) == 0.0
    assert Temperature.celsius_to_kelvin(0.0) == 273.15
    assert Temperature.celsius_to_kelvin(Temperature.kelvin_to_celsius(300.0)) == 300.0


def test_wind_speed_from_components():
    assert Wind.speed(3.0, 4.0) == 5.0
    assert Wind.speed(0.0, 0.0) == 0.0
    assert Wind.speed(-10.0, 0.0) == math.sqrt(100.0)
