"""
Atmospheric Complexity Framework (ACF)

Physical Parameter Representation
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class PhysicalParameter:
    """
    Représentation canonique d'un paramètre physique ou météorologique dans ACF.
    """

    key: str
    name: str
    symbol: str
    domain: str
    unit: str
    description: str
    physical_meaning: str
    dependencies: List[str] = field(default_factory=list)
    related_laws: List[str] = field(default_factory=list)
    calculation_methods: List[str] = field(default_factory=list)

    def summary(self) -> Dict[str, Any]:
        """
        Retourne un dictionnaire résumant les propriétés du paramètre.
        """
        return {
            "key": self.key,
            "name": self.name,
            "symbol": self.symbol,
            "domain": self.domain,
            "unit": self.unit,
            "description": self.description,
            "physical_meaning": self.physical_meaning,
            "dependencies": self.dependencies,
            "related_laws": self.related_laws,
            "calculation_methods": self.calculation_methods,
        }
