"""
Cryosphere Science Encyclopedia Domain
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

ENTRIES = [
    EncyclopediaEntry(
        key="snow_albedo_feedback",
        name="Rétroaction Albédo-Neige",
        domain="Cryosphère",
        subdomain="Bilan d'énergie de la cryosphère",
        equation="alpha_snow = alpha_fresh * exp(-k * age) + alpha_wet * (1 - exp(-k * age))",
        latex_equation=r"\alpha_{\text{snow}} = \alpha_{\text{fresh}} e^{-k t} + \alpha_{\text{wet}} (1 - e^{-k t})",
        variables={"alpha_fresh": "Albédo neige fraîche (~0.85)", "alpha_wet": "Albédo neige fondante (~0.50)"},
        units={"alpha": "dimensionless"},
        description="Diminution de l'albédo de la neige avec le vieillissement et la fonte, accentuant le réchauffement radiatif de la surface.",
        application_conditions=["Surfaces recouvertes de neige"],
        limitations=["Dépend du dépôt de suie / carbone noir"],
        references=["WMO Cryosphere Reports", "Wiscombe & Warren (1980) J. Atmos. Sci."],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
