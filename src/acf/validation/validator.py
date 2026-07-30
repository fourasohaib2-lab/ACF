"""
Atmospheric Complexity Framework (ACF)

VALIDATION - Validator

Purpose:
--------
Dataset and model validation rules engine.

Responsibilities:
-----------------
• Manage validator logic and state representations.
• Integrate with the validation subsystem of the ACF scientific engine.

Major Components:
-----------------
• ParameterValidator

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


class ParameterValidator:

    def __init__(self):

        self.rules = {}

    ####################################

    def register(self, rule: ValidationRule):

        self.rules[rule.parameter] = rule

    ####################################

    def validate(self, parameter, value):

        rule = self.rules.get(parameter)

        if rule is None:
            return True

        if value is None:
            return False

        if rule.minimum is not None and value < rule.minimum:
            return False

        if rule.maximum is not None and value > rule.maximum:
            return False

        return True
