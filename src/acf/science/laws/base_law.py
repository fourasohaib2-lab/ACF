"""
Atmospheric Complexity Framework (ACF)

Scientific Knowledge Engine - Base Law Representation
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class AtmosphericLaw:
    """
    Représentation d'une loi scientifique physique, thermodynamique, aéronautique ou mathématique.
    """

    key: str
    name: str
    domain: str
    equation: str
    variables: Dict[str, str] = field(default_factory=dict)
    units: Dict[str, str] = field(default_factory=dict)
    description: str = ""
    references: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    compute_func: Optional[Callable[..., Any]] = None

    def calculate(self, **kwargs) -> Any:
        """
        Évalue numériquement la loi scientifique avec les paramètres fournis.
        """
        if self.compute_func is None:
            raise NotImplementedError(
                f"Calcul numérique non configuré pour la loi '{self.name}'."
            )
        return self.compute_func(**kwargs)

    def summary(self) -> Dict[str, Any]:
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
