"""
Scientific Reasoning Engine (Physics AI Expert System)
"""

from typing import Any, Dict, List
from acf.science.encyclopedia.knowledge_graph.graph_engine import KnowledgeGraphEngine


class ScientificReasoningEngine:
    """
    Moteur de raisonnement expert physique et d'explication prédictive.
    """

    def __init__(self):
        self.graph = KnowledgeGraphEngine()

    def explain_forecast_chain(self, initial_state: Dict[str, float]) -> Dict[str, Any]:
        """
        Explique la chaîne physique de prévision à partir d'un état atmosphérique initial.
        """
        cape = initial_state.get("cape", 0.0)
        rh = initial_state.get("rh", 50.0)

        chain: List[str] = []
        mechanisms: List[str] = []

        if cape > 1500:
            chain.append("CAPE élevé (> 1500 J/kg)")
            chain.append("Forte instabilité thermodynamique")
            mechanisms.append("Poussée d'Archimède positive accélérant la parcelle d'air")
            
            chain.append("Convection profonde")
            mechanisms.append("Formation d'un courant ascendant rapide (w > 20 m/s)")
            
            chain.append("Cumulonimbus")
            mechanisms.append("Franchissement du LFC et de la tropopause (sommet > 12 km)")
            
            chain.append("Foudre & Electrification")
            mechanisms.append("Collisions non-inductives glace-graupel et séparation de charges")

            if rh > 75:
                chain.append("Fortes précipitations & Grêle")
                mechanisms.append("Accrétion et condensation soutenue par l'humidité de surface")
        else:
            chain.append("CAPE faible à modéré (< 1000 J/kg)")
            chain.append("Stabilité relative / Convection peu profonde")

        return {
            "initial_state": initial_state,
            "casual_chain": chain,
            "physical_mechanisms": mechanisms,
            "explanation": " -> ".join(chain),
        }
