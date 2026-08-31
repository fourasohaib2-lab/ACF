"""
Atmospheric Complexity Framework (ACF)

Weather Research and Forecasting (WRF) Model Encyclopedia Module (ARW & WPS)
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

ENTRIES = [
    EncyclopediaEntry(
        key="nwp_wrf_arw_specifications",
        name="Spécifications du Modèle WRF-ARW (Advanced Research WRF)",
        domain="Modèles Numériques NWP",
        subdomain="WRF Model",
        equation="Fully compressible non-hydrostatic Euler equations with mass-based eta vertical coordinate",
        latex_equation=r"\frac{\partial \mathbf{U}}{\partial t} + (\nabla \cdot \mathbf{U}\mathbf{v}) + \nabla \phi^\prime + \alpha^\prime \nabla p^\prime = \mathbf{F}",
        variables={
            "Résolution": "Flexible (100m à 100km)",
            "Coordinate": "Mass-based hydrostatic pressure eta coordinate",
            "Cœur": "ARW (NCAR)",
        },
        units={"Résolution": "km", "Coord": "eta"},
        description="Modèle météo méso-échelle communautaire développé par NCAR, NOAA/NCEP et l'US Air Force, très largement utilisé pour la recherche et la prévision opérationnelle régionale.",
        application_conditions=[
            "Prévision régionale, recherche atmosphérique, simulations d'ouragans et d'énergie éolienne"
        ],
        limitations=["Configuration complexe nécessitant un choix méticuleux des schémas physiques"],
        references=["Skamarock et al. (2019) NCAR Technical Note", "NCAR WRF User Guide"],
    ),
    EncyclopediaEntry(
        key="nwp_wrf_wps_system",
        name="Système de Prétraitement WRF (WPS - WRF Preprocessing System)",
        domain="Modèles Numériques NWP",
        subdomain="WRF Model",
        equation="Geogrid -> Ungrib -> Metgrid pipeline",
        latex_equation=r"\text{Raw Data (GRIB)} \xrightarrow{\text{Ungrib}} \text{Intermediate} \xrightarrow{+\text{Geogrid}} \text{Metgrid} \xrightarrow{} \text{real.exe}",
        variables={
            "Geogrid": "Définition du domaine et données de surface (USGS/MODIS)",
            "Ungrib": "Extraction GRIB1/GRIB2 (GFS, ECMWF)",
            "Metgrid": "Interpolation horizontale sur la grille WRF",
        },
        units={"Pipeline": "Stage 1, 2, 3"},
        description="Ensemble des programmes de prétraitement servant à définir la géométrie du domaine, interpoler les données géographiques de surface et découper les conditions aux limites à partir de modèles globaux.",
        application_conditions=["Préparation obligatoire avant l'exécution de real.exe / wrf.exe"],
        limitations=["Sensible au choix de la projection cartographique (Lambert, Mercator, Polaire)"],
        references=["NCAR WPS Technical Documentation", "WRF Preprocessing User Guide"],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
