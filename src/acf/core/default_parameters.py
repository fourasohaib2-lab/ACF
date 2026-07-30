"""
Atmospheric Complexity Framework (ACF)

CORE - Default Parameters

Purpose:
--------
Core application lifecycle, service management, plugin registry, and base configurations.

Responsibilities:
-----------------
• Manage default parameters logic and state representations.
• Integrate with the core subsystem of the ACF scientific engine.

Major Components:
-----------------
• Module functions and constants

Dependencies:
-------------
• Python Standard Library and NumPy/Scientific Python Stack.
• Internal acf.core module infrastructure.

Scientific Context:
-------------------
Provides foundational capabilities for numerical weather prediction, atmospheric data processing,
physical modeling, and spatial-temporal analysis within the Atmospheric Complexity Framework.
"""

from acf.core.parameter import Parameter
from acf.core.parameter_registry import ParameterRegistry


def create_registry():

    registry = ParameterRegistry()

    registry.register(
        Parameter(
            id="t2m",
            name="2 m Temperature",
            units="°C",
            category="Surface",
            renderer="Raster",
            colormap="temperature",
            description="Air temperature at 2 metres"
        )
    )

    registry.register(
        Parameter(
            id="rh",
            name="Relative Humidity",
            units="%",
            category="Surface",
            renderer="Raster",
            colormap="humidity"
        )
    )

    registry.register(
        Parameter(
            id="mslp",
            name="Mean Sea Level Pressure",
            units="hPa",
            category="Surface",
            renderer="Contour",
            colormap="pressure"
        )
    )

    registry.register(
        Parameter(
            id="u10",
            name="10 m U Wind",
            units="m/s",
            category="Wind",
            renderer="Wind",
            colormap="wind"
        )
    )

    registry.register(
        Parameter(
            id="v10",
            name="10 m V Wind",
            units="m/s",
            category="Wind",
            renderer="Wind",
            colormap="wind"
        )
    )

    return registry
