"""
Atmospheric Complexity Framework (ACF)

Scientific Knowledge Engine - Base Law Representation
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AtmosphericLaw:
    """
    Représentation d'une loi scientifique physique, thermodynamique, aéronautique ou mathématique.
    """

    key: str
    name: str
    domain: str
    equation: str
    variables: dict[str, str] = field(default_factory=dict)
    units: dict[str, str] = field(default_factory=dict)
    description: str = ""
    references: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    compute_func: Callable[..., Any] | None = None

    def calculate(self, **kwargs) -> Any:
        """
        Évalue numériquement la loi scientifique avec les paramètres fournis.
        """
        if self.compute_func is None:
            raise NotImplementedError(f"Calcul numérique non configuré pour la loi '{self.name}'.")
        return self.compute_func(**kwargs)

    def summary(self) -> dict[str, Any]:
        """
        Retourne la documentation et les métadonnées complètes de la loi.
        """
        return {
            "key": self.key,
            "name": self.name,
            "domain": self.domain,
            "equation": self.equation,
            "variables": self.variables,
            "units": self.units,
            "description": self.description,
            "references": self.references,
            "limitations": self.limitations,
        }


ScientificLaw = AtmosphericLaw
