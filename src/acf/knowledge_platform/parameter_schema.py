"""
Atmospheric Complexity Framework (ACF)

Meteorological Parameter Schema (Phase 1)
(MeteorologicalParameterSchema dataclass with all 28 mandatory scientific attributes)
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class MeteorologicalParameterSchema:
    """
    Spécification canonique exhaustive à 28 attributs pour chaque paramètre météorologique d'ACF.
    """

    # 1. Nom scientifique officiel
    official_scientific_name: str

    # 2. Noms alternatifs
    alternative_names: List[str] = field(default_factory=list)

    # 3. Code OMM (WMO Code)
    wmo_code: str = ""

    # 4. Nom de convention CF (Climate & Forecast)
    cf_convention_name: str = ""

    # 5. Identifiant GRIB2 (Discipline, Category, Number)
    grib2_identifier: str = ""

    # 6. Nom de variable NetCDF
    netcdf_variable: str = ""

    # 7. Descripteur BUFR
    bufr_descriptor: str = ""

    # 8. Unités SI
    si_units: str = ""

    # 9. Dimensions physiques ([M L T K ...])
    dimensions: str = ""

    # 10. Plages de validité physique
    valid_ranges: str = ""

    # 11. Signification physique
    physical_meaning: str = ""

    # 12. Définition mathématique (texte / LaTeX)
    mathematical_definition: str = ""

    # 13. Équations gouvernantes complètes
    full_governing_equations: str = ""

    # 14. Équations de conservation
    conservation_equations: str = ""

    # 15. Équations diagnostiques
    diagnostic_equations: str = ""

    # 16. Formulations empiriques
    empirical_formulations: List[str] = field(default_factory=list)

    # 17. Approximations numériques
    numerical_approximations: List[str] = field(default_factory=list)

    # 18. Implémentations dans les modèles (IFS, AROME, GFS, ICON, WRF)
    model_implementation: List[str] = field(default_factory=list)

    # 19. Dépendances amont
    dependencies: List[str] = field(default_factory=list)

    # 20. Variables dérivées en aval
    derived_variables: List[str] = field(default_factory=list)

    # 21. Références scientifiques (Peer-reviewed DOI / OMM)
    scientific_references: List[str] = field(default_factory=list)

    # 22. Usage opérationnel en centre météo
    operational_usage: str = ""

    # 23. Procédures de contrôle qualité (QC)
    quality_control_procedures: List[str] = field(default_factory=list)

    # 24. Recommandations de visualisation 2D/3D/4D
    visualization_recommendations: str = ""

    # 25. Seuils typiques d'alerte
    typical_thresholds: Dict[str, str] = field(default_factory=dict)

    # 26. Applications pour la prévision numérique
    forecast_applications: List[str] = field(default_factory=list)

    # 27. Applications pour les études climatiques
    climate_applications: List[str] = field(default_factory=list)

    # 28. Applications pour l'apprentissage automatique (Machine Learning / Surrogate)
    machine_learning_applications: List[str] = field(default_factory=list)

    # Clé canonique interne
    key: str = ""
    domain: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le schéma complet en dictionnaire sérialisable."""
        return {
            "key": self.key,
            "domain": self.domain,
            "official_scientific_name": self.official_scientific_name,
            "alternative_names": self.alternative_names,
            "wmo_code": self.wmo_code,
            "cf_convention_name": self.cf_convention_name,
            "grib2_identifier": self.grib2_identifier,
            "netcdf_variable": self.netcdf_variable,
            "bufr_descriptor": self.bufr_descriptor,
            "si_units": self.si_units,
            "dimensions": self.dimensions,
            "valid_ranges": self.valid_ranges,
            "physical_meaning": self.physical_meaning,
            "mathematical_definition": self.mathematical_definition,
            "full_governing_equations": self.full_governing_equations,
            "conservation_equations": self.conservation_equations,
            "diagnostic_equations": self.diagnostic_equations,
            "empirical_formulations": self.empirical_formulations,
            "numerical_approximations": self.numerical_approximations,
            "model_implementation": self.model_implementation,
            "dependencies": self.dependencies,
            "derived_variables": self.derived_variables,
            "scientific_references": self.scientific_references,
            "operational_usage": self.operational_usage,
            "quality_control_procedures": self.quality_control_procedures,
            "visualization_recommendations": self.visualization_recommendations,
            "typical_thresholds": self.typical_thresholds,
            "forecast_applications": self.forecast_applications,
            "climate_applications": self.climate_applications,
            "machine_learning_applications": self.machine_learning_applications,
        }
