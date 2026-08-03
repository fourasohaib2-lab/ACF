"""
Atmospheric Complexity Framework (ACF)

Physics-Informed AI Architectures (PINN, FNO, GNN, Hybrid AI Physics)
"""

from typing import Any, Dict, List
from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry


class PhysicsInformedAIArchitectures:
    """
    Spécifications et formulations des architectures d'IA scientifique hybride.
    """

    @staticmethod
    def pinn_loss_formulation(data_loss: float, pde_residual_loss: float, lambda_pde: float = 1.0) -> float:
        """
        Formulation de la fonction de perte PINN (Physics-Informed Neural Networks):
        Loss_PINN = Loss_Data + lambda_pde * Loss_PDE_Residual
        """
        return float(data_loss + lambda_pde * pde_residual_loss)

    @staticmethod
    def fourier_neural_operator_specs() -> Dict[str, Any]:
        """Retourne les métadonnées et caractéristiques de l'architecture FNO (Fourier Neural Operator)."""
        return {
            "name": "Fourier Neural Operator (FNO)",
            "domain": "Apprentissage d'opérateurs pour EDP atmosphériques",
            "resolution_invariant": True,
            "spectral_convolution": "R(v) = F^-1( K * F(v) ) dans le domaine de Fourier",
            "speedup_vs_nwp": "1000x - 10000x",
            "references": ["Li et al. (2020) NeurIPS", "FourCastNet (Pathak et al. 2022)"],
        }

    @staticmethod
    def graph_neural_network_weather_specs() -> Dict[str, Any]:
        """Retourne les spécifications des architectures GNN sur grille/maillage (ex: GraphCast)."""
        return {
            "name": "Graph Neural Network for Weather (GNN / GraphCast)",
            "domain": "Prévision numérique du temps basée sur des graphes icosaédriques multi-échelles",
            "architecture": "Encoder-Processor-Decoder avec message passing sur maillage icosaédrique 3D",
            "resolution_invariant": False,
            "accuracy": "Surpasse ECMWF HRES sur 90% des variables de vérification",
            "references": ["Lam et al. (2023) Science (Google DeepMind GraphCast)"],
        }

    @staticmethod
    def hybrid_ai_physics_coupler_specs() -> Dict[str, Any]:
        """Retourne les spécifications des modèles hybrides couplant cœur dynamique et paramétrisations IA."""
        return {
            "name": "Couplage Hybride IA-Physique (Hybrid AI-NWP)",
            "domain": "Substitution des schémas de convection/radiation par des réseaux de neurones",
            "architecture": "Cœur dynamique résolvant les équations de Navier-Stokes + Évaluateurs IA sous-maille",
            "conservation_constraints": "Conservation stricte de la masse, de l'énergie et de l'eau garantie par projection physique",
            "references": ["Rasp et al. (2018) PNAS", "Brenowitz & Bretherton (2018) GRL"],
        }


# ---------------------------------------------------------------------------
# Encyclopedia Entries for Physics-AI
# ---------------------------------------------------------------------------

ENTRIES: List[EncyclopediaEntry] = [
    EncyclopediaEntry(
        key="pinn_physics_informed_neural_network",
        name="Réseau de Neurones Informé par la Physique (PINN)",
        domain="Intelligence Artificielle & Physique",
        subdomain="IA Scientifique & EDP",
        equation="Loss_total = Loss_data + lambda_pde * || N(u) - f ||^2",
        latex_equation=r"\mathcal{L}_{\text{PINN}} = \mathcal{L}_{\text{data}} + \lambda_{\text{pde}} \left\| \frac{\partial u}{\partial t} + \mathbf{V}\cdot\nabla u - \nu \nabla^2 u \right\|^2",
        variables={"Loss_data": "Erreur d'ajustement aux observations", "Loss_pde": "Résidu de l'équation différentielle physique"},
        units={"Loss": "dimensionless"},
        description="Architecture de réseau de neurones incorporant directement les équations aux dérivées partielles atmosphériques (Navier-Stokes, conservation de la masse) dans la fonction de perte via la différentiation automatique.",
        application_conditions=["Reconstitution de champs 3D fluides et assimilation de données physiquement cohérente"],
        limitations=["Optimisation parfois difficile en présence de hauts gradients ou de régimes chaotiques"],
        references=["Raissi et al. (2019) J. Comput. Phys.", "Karniadakis et al. (2021) Nature Reviews Physics"],
    ),
    EncyclopediaEntry(
        key="fourier_neural_operator_fno",
        name="Opérateur Neural de Fourier (FNO / FourCastNet)",
        domain="Intelligence Artificielle & Physique",
        subdomain="Opérateurs spectraux IA",
        equation="v_(l+1)(x) = sigma( W * v_l(x) + F^-1 ( R_l * F(v_l) ) )",
        latex_equation=r"v_{l+1}(x) = \sigma \left( W v_l(x) + \mathcal{F}^{-1} \left( R_l \cdot \mathcal{F}(v_l) \right)(x) \right)",
        variables={"F": "Transformée de Fourier rapide (FFT)", "R_l": "Poids complexes appris dans l'espace des fréquences", "W": "Matrice linéaire"},
        units={"Speedup": "10000x"},
        description="Opérateur neural apprenant directement la cartographie d'une fonction vers une autre fonction entre espaces de Banach. Indépendant de la résolution spatiale du réseau de grille.",
        application_conditions=["Prévision météo mondiale ultra-rapide (FourCastNet / Spherical FNO)"],
        limitations=["Nécessite la périodicité des données ou une projection sphérique appropriée"],
        references=["Li et al. (2020) NeurIPS", "Pathak et al. (2022) FourCastNet (NVIDIA)"],
    ),
    EncyclopediaEntry(
        key="graphcast_gnn_weather",
        name="Graphe de Réseau de Neurones Météorologique (GraphCast - Google DeepMind)",
        domain="Intelligence Artificielle & Physique",
        subdomain="Prévision NWP par IA",
        equation="Message passing sur grille icosaédrique 3D: v_i^(l+1) = phi(v_i^l, sum_j psi(v_i^l, v_j^l, e_ij))",
        latex_equation=r"v_i^{(l+1)} = \phi \left( v_i^{(l)}, \sum_{j \in \mathcal{N}(i)} \psi \left( v_i^{(l)}, v_j^{(l)}, e_{ij} \right) \right)",
        variables={"v_i": "Nœuds atmosphériques (latitude, longitude, altitude)", "e_ij": "Arêtes causales 3D dans l'espace"},
        units={"Accuracy": "Surpasse ECMWF HRES à 0.25°"},
        description="Modèle d'IA de prévision météorologique mondiale haute résolution développé par Google DeepMind opérant sur des graphes icosaédriques multi-échelles pour prédire des centaines de variables atmosphériques en moins d'une minute.",
        application_conditions=["Prévision synoptique mondiale à 10 jours"],
        limitations=["Dépendance stricte de l'entraînement aux réanalyses ERA5 de l'ECMWF"],
        references=["Lam et al. (2023) Science (Google DeepMind GraphCast)"],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
