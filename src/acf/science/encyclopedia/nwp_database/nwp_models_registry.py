"""
Global & Regional NWP Models Database Encyclopedia Module (IFS, AROME, ARPEGE, ICON, WRF, GFS, UKMO UM, GEM, COSMO, HARMONIE, Meso-NH, MPAS)
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

ENTRIES: list[EncyclopediaEntry] = [
    EncyclopediaEntry(
        key="nwp_meteo_france_arpege",
        name="Modèle ARPEGE (Météo-France)",
        domain="Modèles Numériques NWP",
        subdomain="Modèles globaux",
        equation="Équations primitives hydrostatiques spectrales avec étirement de maillage (Transformation de Schmidt)",
        latex_equation=r"\Delta x_{\text{France}} \approx 5 \text{ km}, \quad \Delta x_{\text{Antipodes}} \approx 24 \text{ km}, \quad c = 2.25",
        variables={
            "c": "Facteur d'étirement de maillage de Schmidt (2.25)",
            "Pôle d'étirement": "Centré sur la France (46.5°N, 2.5°E)",
            "Niveaux": "105 niveaux verticaux",
        },
        units={"Résolution": "km"},
        description="Modèle spectral global opérationnel de Météo-France reposant sur un maillage étiré sur la France assurant une très haute résolution sur l'Europe tout en couvrant le globe.",
        application_conditions=[
            "Prévision numérique du temps à moyen terme (0 à 102 heures) et conditions aux limites d'AROME"
        ],
        limitations=["Déformation progressive du maillage vers les antipodes"],
        references=["Courtier & Geleyn (1988) Q. J. R. Meteorol. Soc.", "Météo-France ARPEGE Documentation"],
    ),
    EncyclopediaEntry(
        key="nwp_harmonie_arome_accord",
        name="Système HARMONIE-AROME (Consortium ACCORD)",
        domain="Modèles Numériques NWP",
        subdomain="Modèles régionaux",
        equation="Non-hydrostatic Euler equations with ALADIN/AROME physical parameterizations",
        latex_equation=r"\Delta x = 2.5 \text{ km} / 1.3 \text{ km}",
        variables={"Consortium": "ACCORD (HIRLAM + ALADIN + LACE)", "Résolution": "2.5 km / 1.3 km"},
        units={"Résolution": "km"},
        description="Configuration opérationnelle de prévision numérique régionale partagée par 26 services météorologiques européens (Met Norway, SMHI, FMI, KNMI, DMI, AEMET, Météo-France, etc.).",
        application_conditions=["Prévision numérique à haute résolution à l'échelle convective en Europe"],
        limitations=["Requiert l'assimilation locale des observations radar et d'avions"],
        references=["Bengtsson et al. (2017) Mon. Wea. Rev.", "ACCORD Consortium Documentation"],
    ),
    EncyclopediaEntry(
        key="nwp_meso_nh_crm",
        name="Modèle Meso-NH (CNRS / Météo-France)",
        domain="Modèles Numériques NWP",
        subdomain="Cloud Resolving Models (CRM)",
        equation="Non-hydrostatic anelastic / fully-compressible equations with LIMA 2-moment microphysics",
        latex_equation=r"\Delta x = 10 \text{ m à } 2 \text{ km}",
        variables={"Cœur": "Meso-NH non-hydrostatique", "Microphysique": "ICE3 / ICE4 / LIMA (2-moment aerosol-aware)"},
        units={"Résolution": "m"},
        description="Modèle de recherche méso-échelle atmosphérique et de nuages (CRM/LES) développé par le CNRM (Météo-France) et le Laboratoire d'Aérologie (CNRS).",
        application_conditions=[
            "Recherche scientifique sur la microphysique, les orages, les feux de forêt et la chimie de la couche limite"
        ],
        limitations=["Conçu pour la recherche scientifique (coût computationnel élevé)"],
        references=["Lafore et al. (1998) Ann. Geophys.", "Lac et al. (2018) Geosci. Model Dev."],
    ),
    EncyclopediaEntry(
        key="nwp_mpas_voronoi_mesh",
        name="Model for Prediction Across Scales (MPAS - NCAR)",
        domain="Modèles Numériques NWP",
        subdomain="Modèles à maillage variable",
        equation="Non-hydrostatic equations on a centroidal Voronoi tessellation (CVT)",
        latex_equation=r"\text{Mesh: Voronoi Polygons (3 km to 60 km mesh refinement)}",
        variables={
            "Grille": "Polygon Voronoi mesh (Maillage Voronoi variable)",
            "Résolution": "Raffinement continu local (ex: 60 km -> 3 km)",
        },
        units={"Résolution": "km"},
        description="Modèle atmosphérique et océanique de nouvelle génération de NCAR reposant sur un maillage Voronoi à résolution variable sans raccord ni frontière artificielle.",
        application_conditions=["Simulations globales à haute résolution et prévision d'ensemble"],
        limitations=["Nécessite des solveurs géométriques sur grilles hexagonales/polygonal"],
        references=["Skamarock et al. (2012) Mon. Wea. Rev.", "NCAR MPAS Documentation"],
    ),
    EncyclopediaEntry(
        key="nwp_ukmo_unified_model",
        name="UK Met Office Unified Model (UM)",
        domain="Modèles Numériques NWP",
        subdomain="Modèles globaux et régionaux",
        equation="Non-hydrostatic ENDGame dynamical core on rotated lat-lon grid",
        latex_equation=r"\text{Met Office UM: } \Delta x = 10 \text{ km Global}, \quad 1.5 \text{ km UK}",
        variables={
            "Résolution": "10 km (Global) / 1.5 km (UK)",
            "Niveaux": "70 à 140 niveaux verticaux",
            "Cœur": "ENDGame",
        },
        units={"Résolution": "km"},
        description="Système de prévision numérique intégré du Met Office britannique couvrant les échelles globales, régionales et climatiques.",
        application_conditions=[
            "Prévision synoptique mondiale, prévision haute résolution du Royaume-Uni et modélisation climatique HadGEM"
        ],
        limitations=["Grille latitude-longitude tournée nécessitant des transformations de coordonnées"],
        references=["Wood et al. (2014) Q.J.R. Meteorol. Soc.", "UK Met Office Docs"],
    ),
    EncyclopediaEntry(
        key="nwp_gem_environment_canada",
        name="Global Environmental Multiscale Model (GEM - Environment Canada)",
        domain="Modèles Numériques NWP",
        subdomain="Modèles globaux",
        equation="Non-hydrostatic primitive equations on Yin-Yang grid",
        latex_equation=r"\Delta x = 15 \text{ km Global}, \quad 2.5 \text{ km Regional}",
        variables={"Grille": "Yin-Yang grid", "Résolution": "15 km Global / 2.5 km Régional"},
        units={"Résolution": "km"},
        description="Modèle opérationnel du Service Météorologique du Canada fondé sur une méthode d'intégration spatio-temporelle semi-lagrangienne et semi-implicite sur grille Yin-Yang.",
        application_conditions=["Prévision numérique opérationnelle au Canada et en Amérique du Nord"],
        limitations=["Gestion complexe des zones de chevauchement des sous-domaines Yin et Yang"],
        references=["Côté et al. (1998) Mon. Wea. Rev.", "Environment Canada Documentation"],
    ),
    EncyclopediaEntry(
        key="nwp_cosmo_consortium",
        name="COSMO Model (Consortium for Small-scale Modeling)",
        domain="Modèles Numériques NWP",
        subdomain="Modèles régionaux",
        equation="Non-hydrostatic Euler equations on rotated latitude-longitude grid",
        latex_equation=r"\Delta x = 2.8 \text{ km (COSMO-DE)} / 1.1 \text{ km (MeteoSwiss)}",
        variables={"Résolution": "2.8 km / 1.1 km", "Cœur": "Non-hydrostatique méso-échelle"},
        units={"Résolution": "km"},
        description="Modèle méso-échelle européen haute précision développé par le consortium COSMO (DWD, MeteoSwiss, ARPAE, HNMS, IMGW).",
        application_conditions=["Prévision régionale et locale dans l'Arc Alpin et l'Europe centrale"],
        limitations=["Progressivement remplacé par ICON-D2 et ICON-LAM"],
        references=["Baldauf et al. (2011) Mon. Wea. Rev.", "COSMO Consortium Manuals"],
    ),
    EncyclopediaEntry(
        key="nwp_noaa_gfs_model",
        name="Global Forecast System (NOAA GFS / FV3)",
        domain="Modèles Numériques NWP",
        subdomain="Modèles globaux",
        equation="Finite-Volume Cubed-Sphere Dynamical Core (FV3) at 13 km",
        latex_equation=r"\text{NOAA GFS (FV3 Core)} \quad \Delta x = 13 \text{ km}, \quad 127 \text{ Niveaux}",
        variables={"Cœur": "FV3 (GFDL Finite-Volume Cubed-Sphere)", "Résolution": "13 km (C768)"},
        units={"Résolution": "km"},
        description="Modèle météo global principal de la NOAA (National Oceanic and Atmospheric Administration) ouvert en accès libre dans le monde entier.",
        application_conditions=["Prévision synoptique mondiale, trajectoires de cyclones et conditions aux limites"],
        limitations=["Résolution spatiale plus faible que l'ECMWF IFS (9 km vs 13 km)"],
        references=["NOAA NCEP GFS Documentation", "Lin (2004) Mon. Wea. Rev. (FV3 Core)"],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
