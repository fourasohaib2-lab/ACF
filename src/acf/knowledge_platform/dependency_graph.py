"""
Atmospheric Complexity Framework (ACF)

Parameter & Equation Dependency Graph Module
(ParameterDependencyGraph building DAG dependencies and derived variable calculations)
"""

from typing import Any, Dict, List
from acf.knowledge_platform.parameter_database import GlobalParameterDatabase


class ParameterDependencyGraph:
    """
    Graphe orienté acyclique (DAG) des dépendances et dérivations entre paramètres physiques.
    """

    @classmethod
    def get_dependencies(cls, parameter_key: str) -> List[str]:
        """Retourne la liste des paramètres amont indispensables au calcul."""
        param = GlobalParameterDatabase.get(parameter_key)
        return param.dependencies if param else []

    @classmethod
    def get_derived_variables(cls, parameter_key: str) -> List[str]:
        """Retourne la liste des variables aval calculées à partir de ce paramètre."""
        param = GlobalParameterDatabase.get(parameter_key)
        return param.derived_variables if param else []

    @classmethod
    def build_full_causal_tree(cls, target_key: str) -> Dict[str, Any]:
        """Construit l'arbre complet de dépendance amont d'un paramètre cible."""
        dependencies = cls.get_dependencies(target_key)
        tree = {}
        for dep in dependencies:
            tree[dep] = cls.get_dependencies(dep)

        return {
            "target": target_key,
            "direct_dependencies": dependencies,
            "dependency_tree": tree,
        }
