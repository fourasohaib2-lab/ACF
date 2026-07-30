"""
Numerical Weather Prediction (NWP) Models Encyclopedia Domain
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

ENTRIES = [
    EncyclopediaEntry(
        key="ecmwf_ifs_model",
        name="ECMWF Integrated Forecasting System (IFS)",
        domain="Prévision Numérique du Temps (NWP)",
        subdomain="Modèles déterministes et d'ensemble mondiaux",
        equation="Hydrostatic Spectral Primitive Equations TCo1279 (~9 km)",
        latex_equation=r"\text{IFS Resolution: } \text{T}_{\text{Co}}1279 \text{ L}137",
        variables={"Résolution horizontale": "~9 km déterministe", "Niveaux verticaux": "137 niveaux jusqu'à 0.01 hPa"},
        units={"Résolution": "km"},
        description="Système mondial de prévision numérique haut de gamme du CEPMMT (ECMWF) utilisant une grille spectrale octaédrique.",
        application_conditions=["Prévision synoptique mondiale de 0 à 15 jours et prévision d'ensemble (ENS)"],
        limitations=["Modèle global nécessitant d'importants supercalculateurs et paramétrisations sous-maille"],
        references=["ECMWF IFS Documentation (Cy48r1)", "WMO NWP Progress Reports"],
    ),
    EncyclopediaEntry(
        key="arome_model",
        name="Modèle AROME (Météo-France)",
        domain="Prévision Numérique du Temps (NWP)",
        subdomain="Modèles à haute résolution convectivement explicites",
        equation="Non-hydrostatic Euler equations at 1.3 km resolution",
        latex_equation=r"\Delta x = 1.3 \text{ km}, \quad \Delta t = 45 \text{ s}",
        variables={"Grille": "1.3 km sur la France et domaines Outre-Mer", "Physique": "ICE3 microphysics, EDMF turbulence"},
        units={"Grille": "km"},
        description="Modèle de prévision à très haute résolution de Météo-France résolvant explicitement la convection profonde et les orages.",
        application_conditions=["Prévision à courte échéance (0-48h) des phénomènes dangereux"],
        limitations=["Domaine régional nécessitant les conditions aux limites d'ARPEGE"],
        references=["Seity et al. (2011) Mon. Wea. Rev.", "Météo-France Documentation"],
    ),
    EncyclopediaEntry(
        key="icon_model",
        name="Modèle ICON (DWD / MPI-M)",
        domain="Prévision Numérique du Temps (NWP)",
        subdomain="Modèles mondiaux sur grille icosaédrique",
        equation="Non-hydrostatic equations on triangular icosahedral grid",
        latex_equation=r"\text{ICON-Global: } 13 \text{ km}, \quad \text{ICON-EU: } 6.5 \text{ km}",
        variables={"Grille": "Triangle icosaédrique sans pôle géographique"},
        units={"Grille": "km"},
        description="Modèle global non-hydrostatique développé par le DWD et l'Institut Max-Planck assurant une couverture homogène de la Terre.",
        application_conditions=["Prévision numérique du temps et modélisation du climat"],
        limitations=["Conversion des coordonnées triangulaires vers grilles régulières lat/lon"],
        references=["Zängl et al. (2015) Q.J.R. Meteorol. Soc.", "DWD Technical Reports"],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
