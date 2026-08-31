"""
Atmospheric Complexity Framework (ACF)

Cloud Science Knowledge Engine - Base Data Structures
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CloudProcess:
    """
    Représentation d'un processus physique, microphysique ou thermodynamique nuageux.
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
        Calcule la valeur numérique du processus nuageux.
        """
        if self.compute_func is None:
            raise NotImplementedError(f"Calcul non implémenté pour le processus '{self.name}'.")
        return self.compute_func(**kwargs)

    def summary(self) -> dict[str, Any]:
        """
        Retourne les métadonnées et la documentation complète du processus.
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
