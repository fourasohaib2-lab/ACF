"""
Atmospheric Complexity Framework (ACF)

Dataset Validator
"""

from __future__ import annotations


class DatasetValidator:
    """
    Vérifie qu'un Dataset est exploitable.
    """

    REQUIRED_ATTRIBUTES = (
        "name",
        "variables",
        "dimensions",
        "metadata",
    )

    ############################################################

    def validate(self, dataset):

        errors = []

        for attribute in self.REQUIRED_ATTRIBUTES:

            if not hasattr(dataset, attribute):
                errors.append(f"Missing attribute: {attribute}")

        if errors:
            return False, errors

        if len(dataset.variables) == 0:
            errors.append("No variables found.")

        if len(dataset.dimensions) == 0:
            errors.append("No dimensions found.")

        return len(errors) == 0, errors

    ############################################################

    def is_valid(self, dataset):

        valid, _ = self.validate(dataset)

        return valid

