"""
Atmospheric Complexity Framework (ACF)

Parameter & Equation Dependency Graph Module
(ParameterDependencyGraph building DAG dependencies and derived variable calculations)
"""

from typing import Any

from acf.knowledge_platform.parameter_database import GlobalParameterDatabase


class ParameterDependencyGraph:
    """
    Graphe orienté acyclique (DAG) des dépendances et dérivations entre paramètres physiques.
    """

    @classmethod
    def get_dependencies(cls, parameter_key: str) -> list[str]:
        """Retourne la liste des paramètres amont indispensables au calcul."""
        param = GlobalParameterDatabase.get(parameter_key)
        return param.dependencies if param else []

    @classmethod
    def get_derived_variables(cls, parameter_key: str) -> list[str]:
        """Retourne la liste des variables aval calculées à partir de ce paramètre."""
        param = GlobalParameterDatabase.get(parameter_key)
        return param.derived_variables if param else []

    @classmethod
    def build_full_causal_tree(cls, target_key: str, _visited: frozenset[str] = frozenset()) -> dict[str, Any]:
        """
        Construit l'arbre complet de dépendance amont d'un paramètre cible.

        NOTE (correction, 2026-09-05 audit de continuation - suite au
        finding model4d/acf.aeos, cette fois une vraie erreur de code
        plutôt qu'une valeur fabriquée): cette méthode s'arrêtait
        toujours exactement à 2 niveaux (les dépendances directes de
        la cible, puis les dépendances directes de chacune) quelle que
        soit la profondeur réelle du DAG, malgré le nom/docstring
        promettant un arbre "complet" - vérifié par exécution (avec les
        6 paramètres actuellement enregistrés, aucune chaîne ne dépasse
        2 niveaux, donc le défaut restait invisible en pratique, mais
        l'ajout d'un seul paramètre à 3 niveaux de profondeur l'aurait
        silencieusement tronqué). Récursif jusqu'à la racine du DAG,
        avec protection anti-cycle (les listes `dependencies` de
        `GlobalParameterDatabase` sont saisies à la main, sans garantie
        d'acyclicité) - même schéma que le graphe déjà correct de
        `acf.science.parameters.engine.PhysicalParameterEngine.dependency_tree`.
        """
        if target_key in _visited:
            return {"target": target_key, "direct_dependencies": [], "dependency_tree": [], "cycle_detected": True}

        direct = cls.get_dependencies(target_key)
        next_visited = _visited | {target_key}
        return {
            "target": target_key,
            "direct_dependencies": direct,
            "dependency_tree": [cls.build_full_causal_tree(dep, next_visited) for dep in direct],
        }
