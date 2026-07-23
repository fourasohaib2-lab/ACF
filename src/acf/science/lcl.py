"""
Lifting Condensation Level (LCL)
================================
"""


class LCL:
    """LCL height calculator."""

    @staticmethod
    def calculate(
        temperature_c: float,
        dewpoint_c: float,
    ) -> float:
        """
        Approximate LCL height (m).
        """

        if dewpoint_c > temperature_c:
            raise ValueError(
                "dew point cannot exceed air temperature."
            )

        return 125.0 * (
            temperature_c - dewpoint_c
        )

