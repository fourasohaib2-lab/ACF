"""
Advanced Data Assimilation, Hybrid EnVar, LETKF, VarBC & Observation Operators Encyclopedia Module
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

ENTRIES: list[EncyclopediaEntry] = [
    EncyclopediaEntry(
        key="hybrid_envar_data_assimilation",
        name="Assimilation Variationnelle-Ensemble Hybride (Hybrid EnVar)",
        domain="Assimilation de Données",
        subdomain="Méthodes hybrides",
        equation="B_hybrid = alpha * B_static + (1 - alpha) * P_ensemble",
        latex_equation=r"\mathbf{B}_{\text{hybride}} = \alpha \mathbf{B}_{\text{statique}} + (1 - \alpha) \mathbf{P}_{\text{ensemble}}",
        variables={
            "B_static": "Matrice de covariance des erreurs d'ébauche statique climatologique",
            "P_ensemble": "Matrice de covariance dépendante du temps estimée par l'ensemble (EnKF)",
            "alpha": "Facteur de pondération (0.2 à 0.5)",
        },
        units={"alpha": "dimensionless"},
        description="Méthode d'assimilation avancée combinant la stabilité spatiale d'une matrice B statique avec les covariances d'erreur d'ébauche dépendantes de la situation météorologique du jour fournies par un ensemble de prévisions.",
        application_conditions=[
            "Systèmes d'assimilation opérationnels modernes (ECMWF IFS, NOAA GFS/FV3, Météo-France AROME-Ensemble)"
        ],
        limitations=[
            "Nécessite la localisation des covariances d'ensemble pour éliminer le bruit d'échantillonnage à grande distance"
        ],
        references=[
            "Lorenc (2003) Q. J. R. Meteorol. Soc.",
            "Buehner et al. (2010) Mon. Wea. Rev.",
            "WMO Data Assimilation Manual",
        ],
    ),
    EncyclopediaEntry(
        key="letkf_kalman_filter",
        name="Filtre de Kalman d'Ensemble Transformé Local (LETKF)",
        domain="Assimilation de Données",
        subdomain="Filtres d'ensemble",
        equation="Calcul des poids d'ensemble locaux dans l'espace des membres: X_a = X_b * Y_transform",
        latex_equation=r"\mathbf{w}^{(i)} = \left[ (K-1)\mathbf{I} + \mathbf{Y}^{b\,T}\mathbf{R}^{-1}\mathbf{Y}^b \right]^{-1} \mathbf{Y}^{b\,T}\mathbf{R}^{-1}(\mathbf{y} - \bar{\mathbf{y}}^b)",
        variables={
            "Xb": "Perturbations de l'ébauche de l'ensemble",
            "Yb": "Observations simulées par les membres",
            "R": "Matrice de covariance des erreurs d'observation",
        },
        units={"w": "vecteur poids"},
        description="Variante hautement parallélisable du filtre d'EnKF effectuant la mise à jour d'analyse indépendamment pour chaque point de grille en ne retenant que les observations situées dans un rayon de localisation défini.",
        application_conditions=["DWD ICON, JMA, et recherche NWP haute résolution"],
        limitations=["Sensible à la taille du rayon de localisation spatiale"],
        references=["Hunt et al. (2007) Physica D", "DWD ICON-LETKF Manual"],
    ),
    EncyclopediaEntry(
        key="variational_bias_correction_varbc",
        name="Correction Variationnelle des Biais d'Observation (VarBC)",
        domain="Assimilation de Données",
        subdomain="Prétraitement & Qualité",
        equation="y_corrected = y_obs - sum(beta_i * p_i(x))",
        latex_equation=r"\tilde{\mathbf{y}} = \mathbf{y} - \sum_{i=1}^M \beta_i \mathbf{p}_i(\mathbf{x})",
        variables={
            "beta_i": "Predictor coefficients updated continuously inside 3D/4D-Var",
            "p_i": "Predicteurs physiques (ex: angle zénithal, épaisseur de couche)",
        },
        units={"Biais": "Unités d'observation (K, m/s, Pa)"},
        description="Algorithme adaptatif estimant et corrigeant automatiquement les biais systématiques des instruments d'observation (notamment les radiances satellitaires IR/MW) directement au sein du processus de minimisation variationnelle.",
        application_conditions=["Assimilation des radiances satellitaires (Meteosat, GOES, MODIS, NOAA)"],
        limitations=["Risque d'absorption d'erreurs réelles du modèle si les prédicteurs sont mal conditionnés"],
        references=["Dee (2005) Q. J. R. Meteorol. Soc.", "ECMWF VarBC Documentation"],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
