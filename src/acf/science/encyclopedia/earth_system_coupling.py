"""
Earth System Coupling, Climate Feedbacks & Global Cycles Encyclopedia Module
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

ENTRIES: list[EncyclopediaEntry] = [
    EncyclopediaEntry(
        key="earth_system_coupled_model",
        name="Couplage Système Terre (Atmosphère-Océan-Glace-Hydrologie-Biochimie)",
        domain="Sciences du Système Terre",
        subdomain="Couplage multi-composantes",
        equation="Couplage d'échange de flux via un coupleur externe (OASIS3-MCT / CISM)",
        latex_equation=r"\frac{\partial \mathbf{X}_{\text{Earth}}}{\partial t} = \mathbf{F}_{\text{Atmos}} \otimes \mathbf{F}_{\text{Océan}} \otimes \mathbf{F}_{\text{Surface}} \otimes \mathbf{F}_{\text{Cryo}}",
        variables={"OASIS3-MCT": "Coupleur universel de flux massiques et thermiques"},
        units={"Flux": "W/m², kg/(m²·s)"},
        description="Architecture d'intégration globale couplant simultanément la dynamique atmosphérique, l'océan profond (NEMO), la glace de mer (CICE), l'hydrologie continentale (SURFEX/Trip) et les cycles biogéochimiques du carbone (IPSL-CM, CNRM-ESM).",
        application_conditions=["Simulations climatiques globales du GIEC / IPCC CMIP6"],
        limitations=["Nécessite la conservation exacte de la masse et de l'énergie sans dérive de flux à long terme"],
        references=["Valcke (2013) Geosci. Model Dev. (OASIS3-MCT)", "IPCC AR6 Working Group I"],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
