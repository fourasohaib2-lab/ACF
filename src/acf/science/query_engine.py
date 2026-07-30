"""
Atmospheric Complexity Framework (ACF)

Scientific Query Engine (System Expert & Physical AI Ask Interface)
"""

from typing import Any, Dict
from acf.science.encyclopedia.registry import EncyclopediaRegistry
from acf.science.encyclopedia.knowledge_graph.graph_engine import KnowledgeGraphEngine


class ScientificQueryEngine:
    """
    Moteur d'interrogation scientifique naturelle et explicative d'ACF.
    """

    def __init__(self):
        self.graph = KnowledgeGraphEngine()

    def ask(self, question: str) -> Dict[str, Any]:
        """
        Répond scientifiquement à une question en fournissant l'explication physique, les équations, les paramètres, les références et la chaîne causale.
        """
        q = question.lower()

        source_concept = "cape"
        target_concept = "grêle"

        if "cumulonimbus" in q and "grêle" in q:
            source_concept = "cumulonimbus"
            target_concept = "grêle"
        elif "foudre" in q or "éclair" in q:
            source_concept = "cape"
            target_concept = "foudre"
        elif "pluie" in q or "précipitation" in q:
            source_concept = "cape"
            target_concept = "fortes précipitations"

        chain_info = self.graph.explain_chain(source_concept, target_concept)

        # Search matching encyclopedia entries
        matched_entries = EncyclopediaRegistry.search("grêle") if "grêle" in q else EncyclopediaRegistry.search("cumulonimbus")
        equations = [e.latex_equation for e in matched_entries if e.latex_equation]
        references = []
        for e in matched_entries:
            references.extend(e.references)
        references = list(set(references))

        explanation_text = (
            f"Un {source_concept} produit de la {target_concept} lorsque l'énergie convective (CAPE) génère "
            f"un courant ascendant très rapide (w_max > 25 m/s). Les embryons de grêlons (graupels) sont maintenus "
            f"en suspension dans la zone de phase mixte (-10°C à -25°C) où ils capturent par accrétion "
            f"des gouttelettes d'eau surfronde (givrage humide), augmentant de taille jusqu'à ce que leur poids dépasse la sustentation."
        )

        return {
            "question": question,
            "physical_explanation": explanation_text,
            "causal_chain": chain_info.get("explanation", ""),
            "detailed_chain_steps": chain_info.get("chain", []),
            "equations": equations if equations else [r"z_{\text{LCL}} = 125(T-T_d)", r"\text{CAPE} = \int g \frac{T_v - T_{ve}}{T_{ve}} dz"],
            "parameters": {
                "CAPE": "J/kg (Énergie potentielle d'ascendance)",
                "Updraft_w_max": "m/s (Vitesse maximale du courant ascendant)",
                "Freezing_level": "m (Altitude du niveau 0°C)",
            },
            "references": references if references else ["WMO International Cloud Atlas (2017)", "Knight & Knight (2001) Hailstorm Physics", "Pruppacher & Klett (1997)"],
        }


def ask(question: str) -> Dict[str, Any]:
    """
    Fonction raccourci globale acf.science.ask().
    """
    engine = ScientificQueryEngine()
    return engine.ask(question)
