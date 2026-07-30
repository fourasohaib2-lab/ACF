"""
Atmospheric Complexity Framework (ACF)

VALIDATION - Default Rules

Purpose:
--------
Dataset and model validation rules engine.

Responsibilities:
-----------------
• Manage default rules logic and state representations.
• Integrate with the validation subsystem of the ACF scientific engine.

Major Components:
-----------------
• Module functions and constants

Dependencies:
-------------
• Python Standard Library and NumPy/Scientific Python Stack.
• Internal acf.validation module infrastructure.

Scientific Context:
-------------------
Provides foundational capabilities for numerical weather prediction, atmospheric data processing,
physical modeling, and spatial-temporal analysis within the Atmospheric Complexity Framework.
"""

from acf.validation.rule import ValidationRule
from acf.validation.validator import ParameterValidator


def create_validator():

    validator = ParameterValidator()

    validator.register(
        ValidationRule(
            parameter="t2m",
            minimum=180,
            maximum=340,
            units="K"
        )
    )

    validator.register(
        ValidationRule(
            parameter="rh",
            minimum=0,
            maximum=100,
            units="%"
        )
    )

    validator.register(
        ValidationRule(
            parameter="mslp",
            minimum=85000,
            maximum=110000,
            units="Pa"
        )
    )

    validator.register(
        ValidationRule(
            parameter="wind_speed",
            minimum=0,
            maximum=150,
            units="m s-1"
        )
    )

    validator.register(
        ValidationRule(
            parameter="tp",
            minimum=0,
            maximum=5000,
            units="mm"
        )
    )

    return validator
