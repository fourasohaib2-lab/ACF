"""
Satellite Missions, Instruments, Channels & Products Encyclopedia Module
"""

from typing import List
from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

ENTRIES: List[EncyclopediaEntry] = [
    EncyclopediaEntry(
        key="eumetsat_mtg_fci_li",
        name="Météosat Troisième Génération (EUMETSAT MTG - FCI & LI)",
        domain="Télédétection Satellitaire",
        subdomain="Satellites géostationnaires",
        equation="Imagerie FCI (Flexible Combined Imager - 16 canaux, 0.5-2 km) et Éclairs LI (Lightning Imager)",
        latex_equation=r"\text{MTG-I1} \implies \text{FCI (16 Canaux VIS/IR)} + \text{LI (Détection continue des éclairs)}",
        variables={"FCI": "Flexible Combined Imager", "LI": "Lightning Imager (777.4 nm)"},
        units={"Résolution": "0.5 à 2 km"},
        description="Nouvelle génération de satellites géostationnaires européens d'EUMETSAT offrant des images haute fréquence (toutes les 10 min en mode globe et 2.5 min sur l'Europe) et une cartographie continue de la foudre optique.",
        application_conditions=["Prévision immédiate des orages violents (Nowcasting) et surveillance du climat"],
        limitations=["Zone de couverture centrée sur l'Europe et l'Afrique (0 deg Longitude)"],
        references=["EUMETSAT MTG User Documentation (2023)", "Grandell et al. (2019) BAMS"],
    ),
    EncyclopediaEntry(
        key="noaa_goes_r_series_abi",
        name="NOAA GOES-R Series (Advanced Baseline Imager - ABI)",
        domain="Télédétection Satellitaire",
        subdomain="Satellites géostationnaires",
        equation="16 canaux spectraux (2 VIS, 4 NIR, 10 IR) à résolution spatiale 0.5 km à 2 km",
        latex_equation=r"\text{GOES-16/17/18} \implies \text{ABI (16 Canaux)} + \text{GLM (Geostationary Lightning Mapper)}",
        variables={"ABI": "Advanced Baseline Imager", "GLM": "Geostationary Lightning Mapper"},
        units={"Résolution": "0.5 à 2 km"},
        description="Génération moderne de satellites géostationnaires de la NOAA couvrant les Amériques et l'Océan Pacifique avec des rafraîchissements toutes les 30 secondes en mode méso-échelle.",
        application_conditions=["Suivi des cyclones tropicaux, des feux de forêt et des tornades aux USA"],
        limitations=["Couverture limitée à l'hémisphère Ouest"],
        references=["Schmit et al. (2017) Bull. Amer. Meteor. Soc.", "NOAA GOES-R Series Product Manual"],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
