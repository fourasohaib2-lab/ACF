"""
Atmospheric Chemistry & Photochemistry Encyclopedia Module
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

ENTRIES = [
    EncyclopediaEntry(
        key="chapman_stratospheric_cycle",
        name="Cycle Photochimique de Chapman (Ozone Stratosphérique)",
        domain="Chimie Atmosphérique",
        subdomain="Photo-chimie de l'ozone",
        equation="O2 + hnu -> O + O ; O + O2 + M -> O3 + M ; O3 + hnu -> O2 + O ; O + O3 -> 2 O2",
        latex_equation=r"\text{O}_2 + h\nu \rightarrow 2\text{O}, \quad \text{O} + \text{O}_2 + \text{M} \rightarrow \text{O}_3 + \text{M}",
        variables={"hnu": "Rayonnement UV solaire (lambda < 242 nm)"},
        units={"O3": "DU (Dobson Units)"},
        description="Ensemble de réactions photochimiques fondamentales expliquant la formation et le maintien de la couche d'ozone stratosphérique absorbeuse d'UV.",
        application_conditions=["Stratosphère (15-50 km altitude)"],
        limitations=["Formulation pure sans cycles catalytiques de destruction (HOx, NOx, ClOx, BrOx)"],
        references=["Chapman (1930) Mem. R. Meteorol. Soc.", "Seinfeld & Pandis (2016)"],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
