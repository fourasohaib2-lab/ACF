"""
Atmospheric Complexity Framework (ACF)

PARAMETERS - Parameter

Purpose:
--------
Physical parameter definitions, unit conversion tables, and parameter aliases.

Responsibilities:
-----------------
• Manage parameter logic and state representations.
• Integrate with the parameters subsystem of the ACF scientific engine.

Major Components:
-----------------
• Parameter

Dependencies:
-------------
• Python Standard Library and NumPy/Scientific Python Stack.
• Internal acf.parameters module infrastructure.

Scientific Context:
-------------------
Provides foundational capabilities for numerical weather prediction, atmospheric data processing,
physical modeling, and spatial-temporal analysis within the Atmospheric Complexity Framework.
"""

from dataclasses import dataclass


@dataclass
class Parameter:

    code: str
    name: str
    unit: str
    standard_name: str
    category: str
