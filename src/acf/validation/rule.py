"""
Atmospheric Complexity Framework (ACF)

VALIDATION - Rule

Purpose:
--------
Dataset and model validation rules engine.

Responsibilities:
-----------------
• Manage rule logic and state representations.
• Integrate with the validation subsystem of the ACF scientific engine.

Major Components:
-----------------
• ValidationRule

Dependencies:
-------------
• Python Standard Library and NumPy/Scientific Python Stack.
• Internal acf.validation module infrastructure.

Scientific Context:
-------------------
Provides foundational capabilities for numerical weather prediction, atmospheric data processing,
physical modeling, and spatial-temporal analysis within the Atmospheric Complexity Framework.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class ValidationRule:

    parameter: str

    minimum: float | None = None

    maximum: float | None = None

    units: str = ""
