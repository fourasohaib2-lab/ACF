"""
Atmospheric Complexity Framework (ACF)

Atmospheric Scientific Encyclopedia Engine - Base Entry Model
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class EncyclopediaEntry:
    """
    Représentation d'une entrée scientifique computationnelle dans l'encyclopédie ACF.
    """

    key: str
    name: str
    domain: str
    subdomain: str = ""
    equation: str = ""
    latex_equation: str = ""
    variables: Dict[str, str] = field(default_factory=dict)
    units: Dict[str, str] = field(default_factory=dict)
    description: str = ""
    application_conditions: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    compute_func: Optional[Callable[..., Any]] = None

    def calculate(self, **kwargs) -> Any:
        """
        Évalue numériquement l'équation de l'entrée scientifique si un algorithme est associé.
        """
        if self.compute_func is None:
            raise NotImplementedError(f"Calcul non disponible pour l'entrée '{self.name}'.")
        return self.compute_func(**kwargs)

    def summary(self) -> Dict[str, Any]:
        """
        Retourne les métadonnées résumées de l'entrée encyclopédique.
        """
        return {
            "key": self.key,
            "name": self.name,
            "domain": self.domain,
            "subdomain": self.subdomain,
            "equation": self.equation,
            "latex_equation": self.latex_equation,
            "variables": self.variables,
            "units": self.units,
            "description": self.description,
            "application_conditions": self.application_conditions,
            "limitations": self.limitations,
            "references": self.references,
        }
