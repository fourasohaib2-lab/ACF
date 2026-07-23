from dataclasses import dataclass


@dataclass(slots=True)
class ValidationRule:

    parameter: str

    minimum: float | None = None

    maximum: float | None = None

    units: str = ""
