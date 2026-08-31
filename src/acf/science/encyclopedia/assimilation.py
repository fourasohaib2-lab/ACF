"""
Data Assimilation Encyclopedia Domain
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

ENTRIES = [
    EncyclopediaEntry(
        key="four_dimensional_variational_assimilation",
        name="Assimilation Variationnelle Quadridimensionnelle (4D-Var)",
        domain="Assimilation de Données",
        subdomain="Algorithmes d'optimisation variationnelle",
        equation="J(x0) = 0.5*(x0 - xb)^T B^-1 (x0 - xb) + 0.5*sum (y_i - H_i(x_i))^T R_i^-1 (y_i - H_i(x_i))",
        latex_equation=r"J(\mathbf{x}_0) = \frac{1}{2}(\mathbf{x}_0 - \mathbf{x}_b)^T \mathbf{B}^{-1} (\mathbf{x}_0 - \mathbf{x}_b) + \frac{1}{2}\sum_{i} (\mathbf{y}_i - \mathcal{H}_i(\mathbf{x}_i))^T \mathbf{R}_i^{-1} (\mathbf{y}_i - \mathcal{H}_i(\mathbf{x}_i))",
        variables={
            "x0": "État initial cherché (analyse)",
            "xb": "Ébauche (background)",
            "B": "Matrice de covariance d'erreur de background",
            "y": "Observations",
            "R": "Matrice d'erreur d'observation",
        },
        units={"J": "dimensionless"},
        description="Algorithme ajustant l'état initial du modèle NWP sur une fenêtre temporelle (ex: 12h) en minimisant la fonction coût des écarts aux observations.",
        application_conditions=["Centre de prévision disposant de modèles adjoints et supercalculateurs"],
        limitations=["Coût informatique extrêmement élevé et linéarisation du modèle (opérateur tangent linéaire)"],
        references=["Rabier et al. (2000) Q.J.R. Meteorol. Soc.", "ECMWF Assimilation Documentation"],
    ),
    EncyclopediaEntry(
        key="ensemble_kalman_filter",
        name="Filtre de Kalman d'Ensemble (EnKF)",
        domain="Assimilation de Données",
        subdomain="Méthodes séquentielles probabilistes",
        equation="x_a = x_b + K * (y - H(x_b)) ; K = P_b * H^T * (H * P_b * H^T + R)^-1",
        latex_equation=r"\mathbf{x}_a = \mathbf{x}_b + \mathbf{K} \left(\mathbf{y} - \mathcal{H}(\mathbf{x}_b)\right)",
        variables={"K": "Gain de Kalman", "Pb": "Matrice de covariance estimée par l'ensemble (ex: 50 membres)"},
        units={"x_a": "variable d'état"},
        description="Assimilation séquentielle estimant dynamiquement les erreurs de prévision via un échantillon de simulations d'ensemble.",
        application_conditions=["Systèmes de prévision d'ensemble"],
        limitations=["Bruit d'échantillonnage nécessitant la localisation et l'inflation de covariance"],
        references=["Evensen (1994) J. Geophys. Res.", "Houtekamer & Zhang (2016)"],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
