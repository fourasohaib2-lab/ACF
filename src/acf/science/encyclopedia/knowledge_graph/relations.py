"""
Atmospheric Complexity Framework (ACF)

Knowledge Graph Relation Definitions Module
"""

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class KnowledgeRelation:
    """
    Représentation structurée d'une relation causale orientée entre deux nœuds du graphe.
    """

    source: str
    target: str
    relation_type: str = "leads_to"
    cause: str = ""
    equation: str = ""
    domain: str = "Physique Atmosphérique"
    reference: str = "WMO Atmospheric Sciences Manual"

    def to_dict(self) -> Dict[str, Any]:
        """Convertit la relation en dictionnaire."""
        return {
            "source": self.source,
            "target": self.target,
            "relation_type": self.relation_type,
            "cause": self.cause,
            "equation": self.equation,
            "domain": self.domain,
            "reference": self.reference,
        }
