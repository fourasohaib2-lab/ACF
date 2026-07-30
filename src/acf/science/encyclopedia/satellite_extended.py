"""
Advanced Satellite Remote Sensing Encyclopedia Module
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

ENTRIES = [
    EncyclopediaEntry(
        key="cloud_top_temperature_retrieval",
        name="Restitution de la Température du Sommet du Nuage (CTT)",
        domain="Satellites Météorologiques",
        subdomain="Algorithmes satellitaires",
        equation="CTT = B_inv(BT_10.8) for opaque cloud (emissivity ~ 1)",
        latex_equation=r"T_{\text{top}} = B_{10.8}^{-1}(I_{10.8})",
        variables={"BT_10.8": "Température de brillance dans la fenêtre infrarouge 10.8 µm (K)"},
        units={"CTT": "K / °C"},
        description="Méthode de télédétection thermique restituant l'altitude et la température du sommet des nuages épais à partir de l'émission infrarouge.",
        application_conditions=["Nuages optiquement épais (tau > 5)"],
        limitations=["Corrections d'émissivité requises pour les cirrus fins semi-transparents"],
        references=["EUMETSAT NWP SAF Documentation", "NOAA NESDIS Satellite Products"],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
