"""
Advanced Weather Radar Encyclopedia Module
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

ENTRIES = [
    EncyclopediaEntry(
        key="cappi_radar_product",
        name="Plan de Réflectivité à Altitude Constante (CAPPI)",
        domain="Radar Météorologique",
        subdomain="Traitement du signal radar",
        equation="CAPPI(x, y, z0) = Interpolation of elevation PPI sweeps to horizontal plane at altitude z0",
        latex_equation=r"\text{CAPPI}(x,y,z_0) = \mathcal{I}\left(\{\text{PPI}_\theta(r,\phi)\}\right)",
        variables={"z0": "Altitude de la coupe horizontale choisie (ex: 2500 m)"},
        units={"Réflectivité": "dBZ"},
        description="Produit radar standard représentant un plan horizontal continu de réflectivité sans biais de hauteur faisceau.",
        application_conditions=["Réseau de balayages PPI multi-élévations"],
        limitations=["Cône de silence au-dessus du radar et masques du relief"],
        references=["WMO Radar Meteorology Guide", "DWD Radar Products Manual"],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
