"""
Atmospheric Complexity Framework (ACF)

ECMWF Integrated Forecasting System (IFS) Encyclopedia Module
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

ENTRIES = [
    EncyclopediaEntry(
        key="nwp_ecmwf_ifs_specifications",
        name="Spécifications du Modèle ECMWF IFS (Integrated Forecasting System)",
        domain="Modèles Numériques NWP",
        subdomain="ECMWF IFS",
        equation="Équations primitives hydrostatiques spectrales avec assimilation 4D-Var",
        latex_equation=r"\frac{\partial \mathbf{V}_h}{\partial t} + (\mathbf{V}_h \cdot \nabla_h)\mathbf{V}_h + f \mathbf{k}\times\mathbf{V}_h + \nabla_h \Phi + R T \nabla_h \ln p_s = \mathbf{F}_h",
        variables={"Résolution": "TCo1279 (~ 9 km global)", "Niveaux": "137 niveaux verticaux", "Cœur": "Spectral sphérique (Ylm) + Semi-Lagrangien"},
        units={"Résolution": "km", "Niveaux": "137"},
        description="Modèle météo global de référence mondiale développé par l'ECMWF (Centre Européen pour les Prévisions Météorologiques à Moyen Terme). Utilise un développement spectral en harmoniques sphériques et un schéma de transport semi-lagrangien.",
        application_conditions=["Prévision numérique globale à moyen terme (0 à 15 jours) et prévision d'ensemble (EPS 51 membres)"],
        limitations=["Hypothèse hydrostatique nécessitant une paramétrisation sous-maille de la convection profonde"],
        references=["ECMWF IFS Documentation (Cy48r1/Cy49r1)", "Untch & Hortal (2004) Q. J. R. Meteorol. Soc.", "WMO NWP Reports"],
    ),
    EncyclopediaEntry(
        key="ecmwf_ifs_spectral_transform",
        name="Représentation Spectrale et Transformées de Legendre dans IFS",
        domain="Modèles Numériques NWP",
        subdomain="ECMWF IFS",
        equation="Expansions en harmoniques sphériques Y_lm et grille gaussienne réduite",
        latex_equation=r"A(\lambda, \mu) = \sum_{m=-M}^M \sum_{n=|m|}^N A_n^m P_n^m(\mu) e^{i m \lambda}",
        variables={"Anm": "Coefficients spectraux", "Pnm": "Polynômes associés de Legendre", "lambda": "Longitude", "mu": "sin(latitude)"},
        units={"Coefficients": "complexes"},
        description="Méthode spectrale permettant d'évaluer exactement les dérivés spatiales sans erreur de troncature sur la sphère.",
        application_conditions=["Modèles spectraux globaux (IFS, ARPEGE)"],
        limitations=["Coût quadratique O(N³) des transformées de Legendre à très haute résolution"],
        references=["Durran (2010) Numerical Methods for Fluid Dynamics", "ECMWF Technical Documentation"],
    ),
    EncyclopediaEntry(
        key="ecmwf_ifs_4dvar_system",
        name="Assimilation de Données 4D-Var de l'IFS",
        domain="Modèles Numériques NWP",
        subdomain="ECMWF IFS",
        equation="Fonction coût 4D-Var minimisée sur une fenêtre temporelle de 12 heures",
        latex_equation=r"J(\mathbf{x}_0) = \frac{1}{2}(\mathbf{x}_0 - \mathbf{x}_b)^T \mathbf{B}^{-1} (\mathbf{x}_0 - \mathbf{x}_b) + \frac{1}{2}\sum_{k=0}^K (\mathbf{y}_k - \mathcal{H}_k(\mathcal{M}_{0\to k}(\mathbf{x}_0)))^T \mathbf{R}_k^{-1} (\mathbf{y}_k - \mathcal{H}_k(\mathcal{M}_{0\to k}(\mathbf{x}_0)))",
        variables={"x0": "État initial cherché", "xb": "Ébauche (background)", "M": "Modèle pronostique non-linéaire / tangent linéaire"},
        units={"J": "dimensionless"},
        description="Algorithme d'assimilation de données variationnel à 4 dimensions ajustant la trajectoire du modèle aux observations sur une fenêtre de 12 heures.",
        application_conditions=["Cycle d'analyse opérationnel de l'ECMWF (00Z et 12Z)"],
        limitations=["Nécessite le développement et le maintien du modèle tangent linéaire et adjoint"],
        references=["Rabier et al. (2000) Q. J. R. Meteorol. Soc.", "Courtier et al. (1994)"],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
