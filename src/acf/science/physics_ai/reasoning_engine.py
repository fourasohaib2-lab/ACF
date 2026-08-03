"""
Atmospheric Complexity Framework (ACF)

Scientific Reasoning Engine (Physics-AI Expert System & Explanatory Forecast Engine)
"""

from typing import Any, Dict, List
from acf.science.encyclopedia.knowledge_graph.graph_engine import KnowledgeGraphEngine


class ScientificReasoningEngine:
    """
    Moteur de raisonnement expert physique et d'explication prédictive causale.
    """

    def __init__(self):
        self.graph = KnowledgeGraphEngine()

    def explain_forecast_chain(self, initial_state: Dict[str, float]) -> Dict[str, Any]:
        """
        Explique de manière transparente la chaîne causale physique de prévision à partir d'un état atmosphérique initial.
        
        Exemple de chaîne causale:
        CAPE élevé -> instabilité -> convection -> Cumulonimbus -> foudre -> fortes pluies & grêle
        """
        cape = initial_state.get("cape", 0.0)
        rh = initial_state.get("rh", 50.0)
        cin = initial_state.get("cin", 0.0)
        shear = initial_state.get("shear", 10.0)

        chain: List[str] = []
        mechanisms: List[str] = []
        laws_used: List[str] = []

        if cape > 1500 and cin < 100:
            chain.append("CAPE élevé")
            mechanisms.append("Présence d'une forte énergie potentielle disponible (CAPE > 1500 J/kg)")
            laws_used.append("cape_convective_energy")

            chain.append("instabilité")
            mechanisms.append("Différence de température virtuelle positive entre la parcelle et l'environnement")
            laws_used.append("virtual_temperature")

            chain.append("convection")
            mechanisms.append("Franchissement du LFC et accélération verticale rapide de la parcelle")
            laws_used.append("deep_convection_process")

            chain.append("Cumulonimbus")
            mechanisms.append("Extension verticale jusqu'au niveau d'équilibre EL et formation de l'enclume glacée")
            laws_used.append("wmo_cumulonimbus")

            chain.append("foudre")
            mechanisms.append("Electrification non-inductive par collisions glace-graupel et séparation de charge")
            laws_used.append("non_inductive_cloud_charging")

            if rh > 70:
                chain.append("fortes pluies")
                mechanisms.append("Condensation massive et autoconversion soutenue par le fort contenu en eau")
                laws_used.append("kessler_autoconversion_process")

            if shear > 20:
                chain.append("grêle & supercellule")
                mechanisms.append("Rotation du courant ascendant sous l'effet du fort cisaillement du vent 0-6 km")
                laws_used.append("supercell_thunderstorm")
        else:
            chain.append("CAPE faible ou CIN bloquante")
            mechanisms.append("Inhibition convective freinant l'ascendance thermique")
            chain.append("Stabilité relative / Convection peu profonde")
            laws_used.append("cin_convective_inhibition")

        return {
            "initial_state": initial_state,
            "casual_chain": chain,
            "physical_mechanisms": mechanisms,
            "laws_used": laws_used,
            "explanation": " -> ".join(chain),
        }
