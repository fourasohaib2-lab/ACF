"""
Atmospheric Complexity Framework (ACF)

SCIENCE - Pressure

Purpose:
--------
Pure mathematical and thermodynamic formulations (CAPE, CIN, LCL, vorticity).

Responsibilities:
-----------------
• Manage pressure logic and state representations.
• Integrate with the science subsystem of the ACF scientific engine.

Major Components:
-----------------
• Pressure

Dependencies:
-------------
• Python Standard Library and NumPy/Scientific Python Stack.
• Internal acf.science module infrastructure.

Scientific Context:
-------------------
Provides foundational capabilities for numerical weather prediction, atmospheric data processing,
physical modeling, and spatial-temporal analysis within the Atmospheric Complexity Framework.
"""

class Pressure:

    @staticmethod
    def pa_to_hpa(value):

        return value / 100.0

    @staticmethod
    def hpa_to_pa(value):

        return value * 100.0
