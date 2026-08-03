"""
Atmospheric Complexity Framework (ACF)

Météo-France AROME Model Encyclopedia Module
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

ENTRIES = [
    EncyclopediaEntry(
        key="nwp_meteo_france_arome_specifications",
        name="Spécifications du Modèle AROME (Météo-France)",
        domain="Modèles Numériques NWP",
        subdomain="Météo-France AROME",
        equation="Équations d'Euler non-hydrostatiques avec microphysique ICE3/ICE4 à 1.3 km",
        latex_equation=r"\frac{D\mathbf{V}}{Dt} = -\frac{1}{\rho}\nabla p - \mathbf{g}\mathbf{k} - 2\boldsymbol{\Omega}\times\mathbf{V} + \mathbf{F}_{\text{turb}}",
        variables={"Résolution": "1.3 km (AROME-France) / 500 m (AROME-HD)", "Niveaux": "90 niveaux verticaux", "Cœur": "Meso-NH / ALADIN non-hydrostatique"},
        units={"Résolution": "km", "Niveaux": "90"},
        description="Modèle numérique régional de prévision à très haute résolution de Météo-France. Résout explicitement la convection profonde sans paramétrisation sous-maille des courants ascendants convectifs.",
        application_conditions=["Prévision à courte échéance (0 à 48h) des orages, pluies intenses, grêle et brouillard"],
        limitations=["Domaine régional nécessitant les conditions aux limites fournies par ARPEGE"],
        references=["Seity et al. (2011) Mon. Wea. Rev.", "Brousseau et al. (2016) Geosci. Model Dev.", "Météo-France Documentation"],
    ),
    EncyclopediaEntry(
        key="arome_non_hydrostatic_core",
        name="Cœur Dynamique Non-Hydrostatique d'AROME",
        domain="Modèles Numériques NWP",
        subdomain="Météo-France AROME",
        equation="Équations d'Euler fully compressible avec variable de pression Laprise",
        latex_equation=r"\frac{\partial w}{\partial t} + \mathbf{V} \cdot \nabla w = -\frac{1}{\rho}\frac{\partial p}{\partial z} - g + F_w",
        variables={"w": "Vitesse verticale explicite (m/s)", "p": "Pression totale non-hydrostatique (hPa)"},
        units={"w": "m/s"},
        description="Système d'équations non-hydrostatique permettant de modéliser avec précision les accélérations verticales rapides (w > 25 m/s) au sein des tours convectives.",
        application_conditions=["Résolutions spatiales DX < 2.5 km (échelle convective)"],
        limitations=["Nécessite une gestion rigoureuse des ondes acoustiques (schéma semi-implicite)"],
        references=["Laprise (1992) Mon. Wea. Rev.", "Bubnová et al. (1995) Mon. Wea. Rev."],
    ),
    EncyclopediaEntry(
        key="arome_3dvar_assimilation",
        name="Assimilation de Données 3D-Var Rapid Refresh AROME",
        domain="Modèles Numériques NWP",
        subdomain="Météo-France AROME",
        equation="Cycle d'assimilation 3D-Var toutes les 1 heure à 3 heures",
        latex_equation=r"J(\mathbf{x}) = \frac{1}{2}(\mathbf{x}-\mathbf{x}_b)^T \mathbf{B}^{-1} (\mathbf{x}-\mathbf{x}_b) + \frac{1}{2}(\mathbf{y}-\mathcal{H}(\mathbf{x}))^T \mathbf{R}^{-1} (\mathbf{y}-\mathcal{H}(\mathbf{x}))",
        variables={"Observations": "Radars (doppler & réflectivité), Satellites (IR/WV), Stations, Avions (AMDAR)"},
        units={"Fréquence": "1h à 3h"},
        description="Système d'assimilation variationnel 3D-Var à rafraîchissement rapide assimilant les réflectivités radar Doppler et les températures de brillance satellitaires.",
        application_conditions=["Analyse opérationnelle d'AROME-France"],
        limitations=["Fenêtre temporelle d'assimilation plus courte que le 4D-Var"],
        references=["Brousseau et al. (2011) Q. J. R. Meteorol. Soc.", "Météo-France Documentation"],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
