"""
Atmospheric Complexity Framework (ACF)

Knowledge Graph Physical Reasoning Engine Module
"""

from typing import Any


class KnowledgeReasoningEngine:
    """
    Moteur de raisonnement physique automatisé basé sur le graphe de connaissances.
    """

    def __init__(self, graph_engine: Any | None = None):
        if graph_engine is None:
            from acf.science.encyclopedia.knowledge_graph.graph_engine import KnowledgeGraphEngine

            self.graph = KnowledgeGraphEngine()
        else:
            self.graph = graph_engine

    def explain_causal_path(self, source: str, target: str) -> dict[str, Any]:
        """
        Génère une explication physique pas à pas de la chaîne causale entre un concept source et une cible.
        """
        return self.graph.explain_chain(source, target)

    def analyze_convective_chain(self) -> dict[str, Any]:
        """
        Analyse la chaîne causale canonique complète de la convection orageuse et de la grêle.
        """
        source = "cape"
        target = "grêle"
        return self.explain_causal_path(source, target)
