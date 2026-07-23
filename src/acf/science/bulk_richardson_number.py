"""
Bulk Richardson Number (BRN)
============================
"""


class BulkRichardsonNumber:
    """Bulk Richardson Number calculator."""

    @staticmethod
    def calculate(
        cape: float,
        shear: float,
    ) -> float:
        """
        BRN = 2 * CAPE / shear²
        """

        if shear == 0:
            raise ValueError("shear must not be zero")

        return (2.0 * cape) / (shear ** 2)

    @staticmethod
    def category(value: float) -> str:
        """
        BRN classification.
        """

        if value < 10:
            return "Weak"

        if value <= 45:
            return "Supercell"

        return "Multicell"
