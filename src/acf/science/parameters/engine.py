"""
Atmospheric Complexity Framework (ACF)

Physical Parameter Reasoning Engine
"""

from typing import Any, Dict, List, Optional
from acf.science.parameters.physical_parameter import PhysicalParameter
from acf.science.parameters.definitions import PHYSICAL_PARAMETERS
from acf.science.registry import ScientificRegistry


class ParameterEngine:
    """
    Moteur de raisonnement et d'explication physique des paramètres météorologiques et aéronautiques.
    """

    _parameters: Dict[str, PhysicalParameter] = {}
    _initialized: bool = False

    def __init__(self):
        self._ensure_initialized()

    @classmethod
    def _ensure_initialized(cls):
        if cls._initialized:
            return
        cls._parameters.clear()
        for param in PHYSICAL_PARAMETERS:
            cls._parameters[param.key] = param
        cls._initialized = True

    def register(self, param: PhysicalParameter):
        """
        Enregistre un nouveau paramètre physique.
        """
        self._ensure_initialized()
        self._parameters[param.key] = param

    def get(self, key_or_name: str) -> Optional[PhysicalParameter]:
        """
        Récupère un paramètre physique par sa clé canonique ou son nom.
        """
        self._ensure_initialized()
        if key_or_name in self._parameters:
            return self._parameters[key_or_name]

        query = key_or_name.lower()
        for param in self._parameters.values():
            if param.name.lower() == query or param.key.lower() == query or param.symbol.lower() == query:
                return param
        return None

    def dependencies(self, key_or_name: str) -> List[PhysicalParameter]:
        """
        Retourne la liste des paramètres physiques dont dépend directement ce paramètre.
        """
        param = self.get(key_or_name)
        if param is None:
            return []
        res = []
        for dep_key in param.dependencies:
            dep_param = self.get(dep_key)
            if dep_param:
                res.append(dep_param)
        return res

    def dependents(self, key_or_name: str) -> List[PhysicalParameter]:
        """
        Retourne la liste des paramètres qui dépendent de ce paramètre.
        """
        param = self.get(key_or_name)
        if param is None:
            return []
        target_key = param.key
        res = []
        for p in self._parameters.values():
            if target_key in p.dependencies:
                res.append(p)
        return res

    def related_laws(self, key_or_name: str) -> List[Any]:
        """
        Retourne la liste des lois scientifiques (AtmosphericLaw) associées à ce paramètre.
        """
        param = self.get(key_or_name)
        if param is None:
            return []
        laws = []
        for law_key in param.related_laws:
            law = ScientificRegistry.get(law_key)
            if law:
                laws.append(law)
        return laws

    def explain(self, key_or_name: str) -> Dict[str, Any]:
        """
        Génère une explication physique complète de l'origine, des équations, et des dépendances d'un paramètre.
        """
        param = self.get(key_or_name)
        if param is None:
            raise KeyError(f"Paramètre physique inconnu: '{key_or_name}'")

        direct_deps = [p.name for p in self.dependencies(param.key)]
        direct_dep_keys = [p.key for p in self.dependencies(param.key)]
        downstream = [p.name for p in self.dependents(param.key)]
        downstream_keys = [p.key for p in self.dependents(param.key)]
        laws_info = [
            {"name": law.name, "equation": law.equation, "references": law.references}
            for law in self.related_laws(param.key)
        ]

        return {
            "parameter": param.name,
            "key": param.key,
            "symbol": param.symbol,
            "domain": param.domain,
            "unit": param.unit,
            "description": param.description,
            "physical_meaning": param.physical_meaning,
            "direct_dependencies": direct_deps,
            "direct_dependency_keys": direct_dep_keys,
            "downstream_dependents": downstream,
            "downstream_dependent_keys": downstream_keys,
            "governing_laws": laws_info,
            "calculation_methods": param.calculation_methods,
        }

    def dependency_tree(self, key_or_name: str) -> Dict[str, Any]:
        """
        Construit l'arbre complet des dépendances montantes et des impacts descendants d'un paramètre.
        """
        param = self.get(key_or_name)
        if param is None:
            return {}

        return {
            "parameter": param.key,
            "dependencies": [self.dependency_tree(d) for d in param.dependencies if self.get(d)],
            "dependents": [p.key for p in self.dependents(param.key)],
        }

    def list_parameters(self, domain: Optional[str] = None) -> List[PhysicalParameter]:
        """
        Liste tous les paramètres physiques enregistrés, filtrés optionnellement par domaine.
        """
        self._ensure_initialized()
        if domain is None:
            return list(self._parameters.values())
        dom_lower = domain.lower()
        return [p for p in self._parameters.values() if dom_lower in p.domain.lower()]

    def domains(self) -> List[str]:
        """
        Liste les domaines physiques disponibles.
        """
        self._ensure_initialized()
        return sorted(list(set(p.domain for p in self._parameters.values())))
