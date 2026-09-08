"""
Atmospheric Complexity Framework (ACF)

Scientific Exception Manager Module
"""


class ExceptionManager:
    """Classificateur d'exceptions scientifiques et de tolérance aux pannes."""

    @classmethod
    def classify_exception(cls, exc: Exception) -> str:
        return "PHYSICAL_BOUNDARY_WARN" if "Boundary" in str(exc) else "SYSTEM_RECOVERABLE"
