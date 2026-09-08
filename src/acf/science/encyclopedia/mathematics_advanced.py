"""
Advanced Numerical Mathematics, Finite Elements, Stability Analysis & Automatic Differentiation Encyclopedia Module
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

# ---------------------------------------------------------------------------
# Computational Functions for Numerical Mathematics
# ---------------------------------------------------------------------------


def calculate_cfl_number(u_velocity: float, dt_seconds: float, dx_meters: float) -> float:
    """Calcul du nombre de Courant-Friedrichs-Lewy (CFL) C = u * dt / dx."""
    if dx_meters <= 0.0:
        return 0.0
    return abs(u_velocity) * dt_seconds / dx_meters


# ---------------------------------------------------------------------------
# Encyclopedia Entries
# ---------------------------------------------------------------------------

ENTRIES: list[EncyclopediaEntry] = [
    EncyclopediaEntry(
        key="cfl_stability_condition",
        name="Condition de Stabilité Numérique de Courant-Friedrichs-Lewy (CFL)",
        domain="Mathématiques Numériques NWP",
        subdomain="Stabilité des schémas d'advection",
        equation="C = |u| * dt / dx <= C_max  (C_max <= 1 pour les schémas explicites)",
        latex_equation=r"C = \frac{|u| \Delta t}{\Delta x} \le C_{\text{max}} \le 1.0",
        variables={
            "u": "Vitesse advective maximale (m/s)",
            "dt": "Pas de temps d'intégration (s)",
            "dx": "Résolution de maille spatiale (m)",
        },
        units={"C": "dimensionless"},
        description="Condition de stabilité fondamentale pour les équations aux dérivées partielles hyperboliques explicites. Le domaine de dépendance numérique doit contenir le domaine de dépendance physique.",
        application_conditions=["Solveurs d'advection et dynamiques NWP explicites (ex: Runge-Kutta, Leapfrog)"],
        limitations=[
            "Les schémas semi-lagrangians ou implicites permettent d'affranchir le pas de temps de la limite CFL (C > 1)"
        ],
        references=[
            "Courant, Friedrichs & Lewy (1928) Math. Ann.",
            "Durran (2010) Numerical Methods for Fluid Dynamics",
        ],
        compute_func=calculate_cfl_number,
    ),
    EncyclopediaEntry(
        key="von_neummann_stability_analysis",
        name="Analyse de Stabilité de Von Neumann (Mode de Fourier)",
        domain="Mathématiques Numériques NWP",
        subdomain="Analyse numérique",
        equation="Factor d'amplification |G(k)| <= 1 pour tous les modes de Fourier k",
        latex_equation=r"|G(k, \Delta t)| = \left|\frac{u^{n+1}_k}{u^n_k}\right| \le 1, \quad \forall k",
        variables={"G": "Facteur d'amplification complexe du schéma numérique", "k": "Nombre d'onde spatial"},
        units={"G": "dimensionless"},
        description="Technique d'analyse spectrale linéaire permettant d'évaluer la stabilité ou la divergence de schémas de différences finies appliqués aux équations atmosphériques.",
        application_conditions=["Analyse des schémas de discrétisation temporelle et spatiale"],
        limitations=[
            "Valide strictly pour les équations à coefficients constants à conditions aux limites périodiques"
        ],
        references=["Charney, Von Neumann & Stern (1950)", "Durran (2010)"],
    ),
    EncyclopediaEntry(
        key="finite_element_method_fem",
        name="Méthode des Éléments Finis (FEM) en Dynamique des Fluides",
        domain="Mathématiques Numériques NWP",
        subdomain="Discrétisation spatiale",
        equation="Formulation faible de Galerkin: int_Domain (grad(u) . grad(v)) dOmega = int_Domain (f * v) dOmega",
        latex_equation=r"\int_\Omega \nabla u \cdot \nabla v \, d\Omega = \int_\Omega f v \, d\Omega, \quad \forall v \in V_0",
        variables={
            "u": "Champ solution approximé sur éléments",
            "v": "Fonction test (Galerkin)",
            "Omega": "Domaine spatial",
        },
        units={"Discrétisation": "Éléments non-structurés"},
        description="Méthode de discrétisation variationnelle sur maillages non structurés (triangles, tétraèdres) idéale pour la modélisation au voisinage de reliefs complexes.",
        application_conditions=["Modèles atmosphériques régionaux et de surface sur maillage complexe"],
        limitations=[
            "Nécessite l'inversion de matrices de masse globales à chaque pas de temps (sauf en Éléments Finis Discontinus DGFEM)"
        ],
        references=["Zienkiewicz & Taylor (2000)", "Duchaine et al. (2009)"],
    ),
    EncyclopediaEntry(
        key="automatic_differentiation_ad",
        name="Différenciation Automatique (Automatic Differentiation - AD)",
        domain="Mathématiques Numériques NWP",
        subdomain="Calcul de gradients et adjoints",
        equation="Modes Avant (Dual numbers) et Arrière (Reverse/Backpropagation) pour dJ/dx",
        latex_equation=r"\bar{x}_i = \sum_{j \in \text{Children}(i)} \bar{x}_j \frac{\partial f_j}{\partial x_i}",
        variables={"x": "Variables d'entrée du code", "J": "Fonction coût", "bar_x": "Gradient adjoint accumulé"},
        units={"Gradient": "Unites d'adjoint"},
        description="Ensemble de techniques algorithmiques pour calculer de manière exacte (à la précision machine près) la dérivée d'un code informatique complexe. Indispensable pour construire le code adjoint des modèles 4D-Var.",
        application_conditions=["Génération automatique des modèles adjoints 4D-Var (ex: Tapenade, JAX, PyTorch)"],
        limitations=[
            "Nécessite la gestion exacte de la mémoire des états sauvegardés lors du parcours arrière (checkpoints)"
        ],
        references=["Griewank & Walther (2008) Evaluating Derivatives", "ECMWF Adjoint Manual"],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
