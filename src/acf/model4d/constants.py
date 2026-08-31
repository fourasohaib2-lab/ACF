"""
Atmospheric Complexity Framework (ACF)

MODEL4D - Constants
===================
Physical, thermodynamic, and geophysical constants for 4D atmospheric grids.
"""

from __future__ import annotations

# Gravitational acceleration (m s-2)
GRAVITY: float = 9.80665
G: float = 9.80665

# Earth rotation angular velocity (rad s-1)
OMEGA: float = 7.2921159e-5
EARTH_ROTATION: float = 7.2921159e-5

# Mean Earth radius (m)
EARTH_RADIUS: float = 6371000.0

# Gas constants (J kg-1 K-1)
RD: float = 287.05  # Dry air gas constant
RV: float = 461.50  # Water vapor gas constant

# Specific heat capacities (J kg-1 K-1)
CP: float = 1004.0  # Dry air specific heat at constant pressure
CV: float = 717.0   # Dry air specific heat at constant volume
KAPPA: float = RD / CP
EPSILON: float = RD / RV

# Reference standard atmosphere values
STANDARD_PRESSURE: float = 101325.0       # Pa (1 atm)
STANDARD_TEMPERATURE: float = 288.15     # K (15 °C)
STANDARD_DENSITY: float = 1.225          # kg m-3
P0: float = 100000.0                     # Pa (1000 hPa reference)
T0: float = 273.15                       # K (0 °C)

# Latent heat constants (J kg-1)
LV: float = 2.5e6                        # Vaporization
LF: float = 3.34e5                       # Fusion
LS: float = 2.834e6                      # Sublimation

