"""
Data Assimilation Advanced Encyclopedia Module
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

ENTRIES = [
    EncyclopediaEntry(
        key="cost_function_variational_assimilation",
        name="Fonction Coût des Assimilations Variationnelles (3D-Var / 4D-Var)",
        domain="Assimilation de Données",
        subdomain="Algorithmes variationnels",
        equation="J(x) = (x - xb)^T * B^-1 * (x - xb) + (y - H(x))^T * R^-1 * (y - H(x))",
        latex_equation=r"J(\mathbf{x}) = (\mathbf{x}-\mathbf{x}_b)^T \mathbf{B}^{-1} (\mathbf{x}-\mathbf{x}_b) + (\mathbf{y}-\mathcal{H}(\mathbf{x}))^T \mathbf{R}^{-1} (\mathbf{y}-\mathcal{H}(\mathbf{x}))",
        variables={"x": "Vecteur d'état analysé", "xb": "Background", "B": "Covariance d'erreur de background", "y": "Observations", "R": "Covariance d'erreur d'observation"},
        units={"J": "dimensionless"},
        description="Formulation quadratique minimisée par gradient conjugué ou L-BFGS pour estimer l'état optimal de l'atmosphère.",
        application_conditions=["Centre de prévision NWP opérationnel"],
        limitations=["Sensible au choix des matrices de covariance B et R"],
        references=["Ide et al. (1997) J. Meteor. Soc. Japan", "ECMWF Assimilation Docs"],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
