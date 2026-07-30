"""
Atmospheric Complexity Framework (ACF)

Encyclopedia Scientific Registry
"""

from typing import Any, Dict, List, Optional
from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.registry import ScientificRegistry
from acf.science.laws.base_law import AtmosphericLaw


class EncyclopediaRegistry:
    """
    Registre universel centralisé de l'Encyclopédie Scientifique Atmosphérique ACF.
    """

    _entries: Dict[str, EncyclopediaEntry] = {}
    _initialized: bool = False

    @classmethod
    def _ensure_initialized(cls):
        if cls._initialized:
            return
        cls._initialized = True
        # Lazy import of encyclopedia domain modules

    @classmethod
    def register(cls, entry: EncyclopediaEntry):
        """
        Enregistre une entrée encyclopédique et la synchronise avec ScientificRegistry.
        """
        cls._entries[entry.key] = entry
        # Sync with ScientificRegistry for 100% backward compatibility
        law = AtmosphericLaw(
            key=entry.key,
            name=entry.name,
            domain=entry.domain,
            equation=entry.equation,
            variables=entry.variables,
            units=entry.units,
            description=entry.description,
            references=entry.references,
            limitations=entry.limitations,
            compute_func=entry.compute_func,
        )
        ScientificRegistry.register(law)

    @classmethod
    def get(cls, key_or_name: str) -> Optional[EncyclopediaEntry]:
        """
        Récupère une entrée par sa clé ou son nom.
        """
        cls._ensure_initialized()
        if key_or_name in cls._entries:
            return cls._entries[key_or_name]
        q = key_or_name.lower()
        for entry in cls._entries.values():
            if entry.name.lower() == q or entry.key.lower() == q:
                return entry
        return None

    @classmethod
    def search(cls, query: str) -> List[EncyclopediaEntry]:
        """
        Recherche dans l'encyclopédie par mot-clé.
        """
        cls._ensure_initialized()
        q = query.lower()
        results = []
        for entry in cls._entries.values():
            text = f"{entry.name} {entry.domain} {entry.subdomain} {entry.description} {entry.equation}".lower()
            if q in text:
                results.append(entry)
        return results

    @classmethod
    def list_domain(cls, domain: str) -> List[EncyclopediaEntry]:
        """
        Liste toutes les entrées d'un domaine donné.
        """
        cls._ensure_initialized()
        dom_lower = domain.lower()
        return [e for e in cls._entries.values() if dom_lower in e.domain.lower()]

    @classmethod
    def list_entries(cls) -> List[EncyclopediaEntry]:
        """
        Liste toutes les entrées enregistrées dans l'encyclopédie.
        """
        cls._ensure_initialized()
        return list(cls._entries.values())

    @classmethod
    def domains(cls) -> List[str]:
        """
        Liste la totalité des domaines scientifiques répertoriés.
        """
        cls._ensure_initialized()
        return sorted(list(set(e.domain for e in cls._entries.values())))

    @classmethod
    def calculate(cls, key_or_name: str, **kwargs) -> Any:
        """
        Calcule la valeur numérique associée à une entrée encyclopédique.
        """
        entry = cls.get(key_or_name)
        if entry is None:
            raise KeyError(f"Entrée encyclopédique inconnue: '{key_or_name}'")
        return entry.calculate(**kwargs)

    @classmethod
    def count(cls) -> int:
        """
        Retourne le nombre total d'entrées répertoriées.
        """
        cls._ensure_initialized()
        return len(cls._entries)
