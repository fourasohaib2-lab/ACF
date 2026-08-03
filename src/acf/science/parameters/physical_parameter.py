"""
Atmospheric Complexity Framework (ACF)

Physical Parameter Representation & Comprehensive Metadata Model
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class PhysicalParameter:
    """
    Représentation canonique universelle d'un paramètre physique ou météorologique dans ACF.
    """

    key: str
    name: str
    symbol: str
    domain: str
    unit: str
    description: str
    physical_meaning: str
    aliases: List[str] = field(default_factory=list)
    abbreviation: str = ""
    category: str = ""
    alternative_units: List[str] = field(default_factory=list)
    dimensions: str = ""
    governing_equation: str = ""
    latex_equation: str = ""
    variables: Dict[str, str] = field(default_factory=dict)
    assumptions: List[str] = field(default_factory=list)
    applicability: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    valid_range: str = ""
    cf_standard_name: str = ""
    grib2_code: str = ""
    bufr_code: str = ""
    netcdf_name: str = ""
    observation_systems: List[str] = field(default_factory=list)
    numerical_models: List[str] = field(default_factory=list)
    satellite_products: List[str] = field(default_factory=list)
    radar_products: List[str] = field(default_factory=list)
    aviation_applications: List[str] = field(default_factory=list)
    climatology_applications: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    derived_parameters: List[str] = field(default_factory=list)
    related_laws: List[str] = field(default_factory=list)
    calculation_methods: List[str] = field(default_factory=list)

    def summary(self) -> Dict[str, Any]:
        """
        Retourne un dictionnaire résumant l'ensemble des propriétés et métadonnées du paramètre.
        """
        return {
            "key": self.key,
            "name": self.name,
            "symbol": self.symbol,
            "domain": self.domain,
            "unit": self.unit,
            "description": self.description,
            "physical_meaning": self.physical_meaning,
            "aliases": self.aliases,
            "abbreviation": self.abbreviation,
            "category": self.category,
            "alternative_units": self.alternative_units,
            "dimensions": self.dimensions,
            "governing_equation": self.governing_equation,
            "latex_equation": self.latex_equation,
            "variables": self.variables,
            "assumptions": self.assumptions,
            "applicability": self.applicability,
            "limitations": self.limitations,
            "valid_range": self.valid_range,
            "cf_standard_name": self.cf_standard_name,
            "grib2_code": self.grib2_code,
            "bufr_code": self.bufr_code,
            "netcdf_name": self.netcdf_name,
            "observation_systems": self.observation_systems,
            "numerical_models": self.numerical_models,
            "satellite_products": self.satellite_products,
            "radar_products": self.radar_products,
            "aviation_applications": self.aviation_applications,
            "climatology_applications": self.climatology_applications,
            "references": self.references,
            "dependencies": self.dependencies,
            "derived_parameters": self.derived_parameters,
            "related_laws": self.related_laws,
            "calculation_methods": self.calculation_methods,
        }
