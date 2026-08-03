"""
Atmospheric Complexity Framework (ACF)

Knowledge Graph Node Definitions Module
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class KnowledgeNode:
    """
    Représentation structurée d'un nœud conceptuel dans le graphe de connaissances physiques.
    """

    key: str
    name: str
    domain: str = "Physique Atmosphérique"
    description: str = ""
    equation: str = ""
    latex_equation: str = ""
    variables: Dict[str, str] = field(default_factory=dict)
    units: Dict[str, str] = field(default_factory=dict)
    references: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le nœud en dictionnaire."""
        return {
            "key": self.key,
            "name": self.name,
            "domain": self.domain,
            "description": self.description,
            "equation": self.equation,
            "latex_equation": self.latex_equation,
            "variables": self.variables,
            "units": self.units,
            "references": self.references,
        }
