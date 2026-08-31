"""
Atmospheric Complexity Framework (ACF)

Advanced Data Assimilation Encyclopedia Module (3D-Var, 4D-Var, EnKF & Cost Function)
"""

import numpy as np

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

# ---------------------------------------------------------------------------
# Computational Functions for Data Assimilation
# ---------------------------------------------------------------------------


def calculate_variational_cost_function(
    x: np.ndarray | list[float],
    xb: np.ndarray | list[float],
    b_inv: np.ndarray | list[list[float]],
    y: np.ndarray | list[float],
    hx: np.ndarray | list[float],
    r_inv: np.ndarray | list[list[float]],
) -> float:
    """
    Calcul de la fonction coût des méthodes d'assimilation variationnelles:
    J(x) = 0.5 * (x - xb)^T * B^-1 * (x - xb) + 0.5 * (y - H(x))^T * R^-1 * (y - H(x))
    """
    x_arr = np.asarray(x, dtype=float)
    xb_arr = np.asarray(xb, dtype=float)
    b_inv_arr = np.asarray(b_inv, dtype=float)
    y_arr = np.asarray(y, dtype=float)
    hx_arr = np.asarray(hx, dtype=float)
    r_inv_arr = np.asarray(r_inv, dtype=float)

    dx = x_arr - xb_arr
    dy = y_arr - hx_arr

    j_b = 0.5 * float(np.dot(dx, np.dot(b_inv_arr, dx)))
    j_o = 0.5 * float(np.dot(dy, np.dot(r_inv_arr, dy)))

    return j_b + j_o


# ---------------------------------------------------------------------------
# Encyclopedia Entries
# ---------------------------------------------------------------------------

ENTRIES: list[EncyclopediaEntry] = [
    EncyclopediaEntry(
        key="cost_function_variational_assimilation",
        name="Fonction Coût des Assimilations Variationnelles (3D-Var / 4D-Var)",
        domain="Assimilation de Données",
        subdomain="Algorithmes variationnels",
        equation="J(x) = 0.5 * (x - xb)^T * B^-1 * (x - xb) + 0.5 * (y - H(x))^T * R^-1 * (y - H(x))",
        latex_equation=r"J(\mathbf{x}) = \frac{1}{2}(\mathbf{x}-\mathbf{x}_b)^T \mathbf{B}^{-1} (\mathbf{x}-\mathbf{x}_b) + \frac{1}{2}(\mathbf{y}-\mathcal{H}(\mathbf{x}))^T \mathbf{R}^{-1} (\mathbf{y}-\mathcal{H}(\mathbf{x}))",
        variables={
            "x": "Vecteur d'état analysé",
            "xb": "Ébauche (background)",
            "B": "Covariance d'erreur de background",
            "y": "Vecteur d'observations",
            "H": "Opérateur d'observation",
            "R": "Covariance d'erreur d'observation",
        },
        units={"J": "dimensionless"},
        description="Formulation quadratique objectif minimisée par descente de gradient (L-BFGS ou Conjugate Gradient) pour estimer l'état le plus vraisemblable de l'atmosphère.",
        application_conditions=["Centres de prévision numérique NWP (ECMWF, Météo-France, NOAA, NCEP)"],
        limitations=["Hypothèse d'erreurs gaussiennes non-biaisées"],
        references=[
            "Ide et al. (1997) J. Meteor. Soc. Japan",
            "Lorenc (1986) Q. J. R. Meteorol. Soc.",
            "ECMWF Assimilation Docs",
        ],
        compute_func=calculate_variational_cost_function,
    ),
    EncyclopediaEntry(
        key="three_dimensional_variational_3dvar",
        name="Assimilation Variationnelle 3D-Var",
        domain="Assimilation de Données",
        subdomain="Algorithmes variationnels",
        equation="Minimisation instantanée de J(x) à l'heure d'analyse t0",
        latex_equation=r"J(\mathbf{x}) = \frac{1}{2}(\mathbf{x}-\mathbf{x}_b)^T \mathbf{B}^{-1} (\mathbf{x}-\mathbf{x}_b) + \frac{1}{2}(\mathbf{y}-\mathcal{H}(\mathbf{x}))^T \mathbf{R}^{-1} (\mathbf{y}-\mathcal{H}(\mathbf{x}))",
        variables={"B": "Matrice de covariance statique", "t0": "Temps fixe d'analyse"},
        units={"Time": "t0 fixe"},
        description="Méthode d'assimilation 3D résolvant l'état optimal à un instant donné en combinant l'ébauche et toutes les observations contenues dans la fenêtre d'assimilation ramenées à t0.",
        application_conditions=["AROME 3D-Var, WRF 3DVAR, US NCEP NAM"],
        limitations=["Ne prend pas en compte la dépendance temporelle du modèle au cours de la fenêtre d'assimilation"],
        references=["Parrish & Derber (1992) Mon. Wea. Rev.", "Météo-France / NCAR Documentation"],
    ),
    EncyclopediaEntry(
        key="four_dimensional_variational_4dvar",
        name="Assimilation Variationnelle 4D-Var",
        domain="Assimilation de Données",
        subdomain="Algorithmes variationnels",
        equation="Minimisation de J(x0) en intégrant la trajectoire temporelle du modèle M_{0->k}",
        latex_equation=r"J(\mathbf{x}_0) = \frac{1}{2}(\mathbf{x}_0-\mathbf{x}_b)^T \mathbf{B}^{-1} (\mathbf{x}_0-\mathbf{x}_b) + \frac{1}{2}\sum_{k=0}^K (\mathbf{y}_k-\mathcal{H}_k(\mathcal{M}_{0\to k}(\mathbf{x}_0)))^T \mathbf{R}_k^{-1} (\mathbf{y}_k-\mathcal{H}_k(\mathcal{M}_{0\to k}(\mathbf{x}_0)))",
        variables={"M0->k": "Intégrateur temporel du modèle NWP non-linéaire"},
        units={"Fenêtre": "6h à 12h"},
        description="Méthode d'assimilation de pointe intégrant la dynamique complète du modèle via ses opérateurs tangent linéaire et adjoint, assurant une parfaite cohérence physique des analyses.",
        application_conditions=["ECMWF IFS, Météo-France ARPEGE, Met Office, JMA"],
        limitations=["Extrêmement exigeant en ressources de supercalcul"],
        references=["Rabier et al. (2000) Q. J. R. Meteorol. Soc.", "Courtier et al. (1994)"],
    ),
    EncyclopediaEntry(
        key="ensemble_kalman_filter_enkf",
        name="Filtre de Kalman d'Ensemble (EnKF)",
        domain="Assimilation de Données",
        subdomain="Filtres séquentiels d'ensemble",
        equation="B_ens = 1/(N-1) * sum (x_i - x_mean)(x_i - x_mean)^T,  x_i^a = x_i^b + K (y_i - H x_i^b)",
        latex_equation=r"\mathbf{K} = \mathbf{P}_b \mathcal{H}^T \left(\mathcal{H} \mathbf{P}_b \mathcal{H}^T + \mathbf{R}\right)^{-1}, \quad \mathbf{x}_i^a = \mathbf{x}_i^b + \mathbf{K} \left(\mathbf{y}_i - \mathcal{H}(\mathbf{x}_i^b)\right)",
        variables={
            "Pb": "Covariance des erreurs d'ébauche dépendant du temps (Errors of the day)",
            "K": "Gain de Kalman",
        },
        units={"N": "Nombre de membres de l'ensemble (30 à 100)"},
        description="Méthode probabiliste séquentielle estimant dynamiquement la covariance des erreurs de prévision B à partir d'un ensemble de prévisions numériques propagées en parallèle.",
        application_conditions=["Assimilation d'ensemble (LETKF, ETKF, EnVar hybride)"],
        limitations=[
            "Exige de la localisation de covariance et de l'inflation de variance pour éviter le collapse d'ensemble"
        ],
        references=["Evensen (1994) J. Geophys. Res.", "Houtekamer & Mitchell (1998) Mon. Wea. Rev."],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
