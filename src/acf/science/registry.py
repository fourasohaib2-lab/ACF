"""
Atmospheric Complexity Framework (ACF)

Scientific Knowledge Engine Registry
"""

from acf.science.laws.aeronautics import AERONAUTICAL_LAWS
from acf.science.laws.atmospheric import ATMOSPHERIC_LAWS
from acf.science.laws.base_law import AtmosphericLaw
from acf.science.laws.boundary_layer import BOUNDARY_LAYER_LAWS
from acf.science.laws.dynamics import DYNAMIC_LAWS
from acf.science.laws.geodesy import GEODESY_LAWS
from acf.science.laws.mathematics import MATHEMATICAL_LAWS
from acf.science.laws.microphysics import MICROPHYSICS_LAWS
from acf.science.laws.radiation import RADIATION_LAWS
from acf.science.laws.thermodynamics import THERMODYNAMIC_LAWS


class ScientificRegistry:
    """
    Registre universel des lois scientifiques, physiques, thermodynamiques et mathématiques de ACF.
    """

    _registry: dict[str, AtmosphericLaw] = {}
    _initialized: bool = False

    @classmethod
    def _ensure_initialized(cls):
        if cls._initialized:
            return
        cls._registry.clear()
        all_laws = (
            ATMOSPHERIC_LAWS
            + THERMODYNAMIC_LAWS
            + DYNAMIC_LAWS
            + BOUNDARY_LAYER_LAWS
            + MICROPHYSICS_LAWS
            + RADIATION_LAWS
            + AERONAUTICAL_LAWS
            + MATHEMATICAL_LAWS
            + GEODESY_LAWS
        )
        for law in all_laws:
            cls._registry[law.key] = law
        cls._initialized = True

    @classmethod
    def register(cls, law: AtmosphericLaw):
        """
        Enregistre une nouvelle loi scientifique dans le registre.
        """
        cls._ensure_initialized()
        cls._registry[law.key] = law

    @classmethod
    def get(cls, key_or_name: str) -> AtmosphericLaw | None:
        """
        Récupère une loi par sa clé canonique ou son nom scientifique.
        """
        cls._ensure_initialized()
        if key_or_name in cls._registry:
            return cls._registry[key_or_name]

        query = key_or_name.lower()
        for law in cls._registry.values():
            if law.name.lower() == query or law.key.lower() == query:
                return law
        return None

    @classmethod
    def list_laws(cls, domain: str | None = None) -> list[AtmosphericLaw]:
        """
        Liste toutes les lois enregistrées, filtrées optionnellement par domaine.
        """
        cls._ensure_initialized()
        if domain is None:
            return list(cls._registry.values())
        domain_lower = domain.lower()
        return [law for law in cls._registry.values() if domain_lower in law.domain.lower()]

    @classmethod
    def domains(cls) -> list[str]:
        """
        Retourne la liste des domaines scientifiques disponibles.
        """
        cls._ensure_initialized()
        return sorted({law.domain for law in cls._registry.values()})

    @classmethod
    def search(cls, query: str) -> list[AtmosphericLaw]:
        """
        Recherche des lois scientifiques par mot-clé dans leur nom, description ou équation.
        """
        cls._ensure_initialized()
        q = query.lower()
        results = []
        for law in cls._registry.values():
            text = f"{law.name} {law.domain} {law.equation} {law.description}".lower()
            if q in text:
                results.append(law)
        return results

    @classmethod
    def count(cls) -> int:
        """
        Retourne le nombre total de lois scientifiques enregistrées.
        """
        cls._ensure_initialized()
        return len(cls._registry)
