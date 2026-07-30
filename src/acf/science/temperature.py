"""
Atmospheric Complexity Framework (ACF)

SCIENCE - Temperature

Purpose:
--------
Pure mathematical and thermodynamic formulations (CAPE, CIN, LCL, vorticity).

Responsibilities:
-----------------
• Manage temperature logic and state representations.
• Integrate with the science subsystem of the ACF scientific engine.

Major Components:
-----------------
• Temperature

Dependencies:
-------------
• Python Standard Library and NumPy/Scientific Python Stack.
• Internal acf.science module infrastructure.

Scientific Context:
-------------------
Provides foundational capabilities for numerical weather prediction, atmospheric data processing,
physical modeling, and spatial-temporal analysis within the Atmospheric Complexity Framework.
"""

class Temperature:

    @staticmethod
    def kelvin_to_celsius(value):

        return value - 273.15

    @staticmethod
    def celsius_to_kelvin(value):

        return value + 273.15
