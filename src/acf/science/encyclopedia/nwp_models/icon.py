"""
Atmospheric Complexity Framework (ACF)

ICON (ICOsahedral Nonhydrostatic) Model Encyclopedia Module (DWD / MPI-M)
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

ENTRIES = [
    EncyclopediaEntry(
        key="nwp_dwd_icon_specifications",
        name="Spécifications du Modèle ICON (DWD / MPI-M)",
        domain="Modèles Numériques NWP",
        subdomain="DWD ICON",
        equation="Non-hydrostatic equations on a geodesic icosahedral-triangular grid",
        latex_equation=r"\frac{\partial v_n}{\partial t} + \frac{\partial K}{\partial n} + (\zeta + f) v_t + w \frac{\partial v_n}{\partial z} = -\frac{1}{\rho}\frac{\partial p}{\partial n}",
        variables={
            "Grid": "Icosahedral triangular grid (grille triangulaire icosaédrique)",
            "Résolution": "13 km (ICON global) / 2.1 km (ICON-D2)",
        },
        units={"Résolution": "km"},
        description="Modèle météo de nouvelle génération développé conjointement par le DWD (Deutscher Wetterdienst) et le Max Planck Institute (MPI-M) reposant sur une grille icosaédrique non-hydrostatique à mailles triangulaires sans singularités polaires.",
        application_conditions=["Prévision numérique globale et régionale d'Allemagne/Europe"],
        limitations=["Discrétisation spatiale complexe sur grille non-structurée"],
        references=["Zängl et al. (2015) Q. J. R. Meteorol. Soc.", "DWD ICON Documentation"],
    ),
    EncyclopediaEntry(
        key="dwd_icon_icosahedral_grid",
        name="Grille Icosaédrique et Discrétisation d'ICON",
        domain="Modèles Numériques NWP",
        subdomain="DWD ICON",
        equation="Division successive de l'icosaèdre régulier en triangles sphériques (R2B06, R3B07)",
        latex_equation=r"N_{\text{triangles}} = 20 \times n_{\text{root}}^2 \times 4^{\text{bisect}}",
        variables={
            "N_triangles": "Nombre de cellules triangulaires",
            "v_n": "Vitesse normale aux arêtes des triangles",
        },
        units={"Cellules": "millions"},
        description="Grille géodésique uniforme couvrant la sphère terrestre sans pincement polaire, évitant les problèmes de CFL aux pôles propres aux grilles latitude-longitude.",
        application_conditions=["Modelisation globale d'ICON et rémanences régionales emboîtées (nesting)"],
        limitations=["Nécessite des algorithmes de post-traitement pour ré-échantillonner sur grille lat-lon standard"],
        references=["Dipankar et al. (2015) Mon. Wea. Rev.", "DWD Technical Reports"],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
