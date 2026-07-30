"""
Météo-France AROME Model Encyclopedia Documentation Module
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

ENTRY = EncyclopediaEntry(
    key="nwp_meteo_france_arome_specifications",
    name="Spécifications Modèle AROME (Météo-France)",
    domain="Modèles Numériques NWP",
    subdomain="Météo-France AROME",
    equation="Non-hydrostatic Euler equations with ICE3/ICE4 microphysics at 1.3 km",
    latex_equation=r"\frac{D\mathbf{V}}{Dt} = -\frac{1}{\rho}\nabla p - \mathbf{g}\mathbf{k} - 2\boldsymbol{\Omega}\times\mathbf{V} + \mathbf{F}_{\text{turb}}",
    description="Modèle régional non-hydrostatique résolvant explicitement la convection profonde.",
    references=["Seity et al. (2011) Mon. Wea. Rev.", "Météo-France Documentation"],
)

EncyclopediaRegistry.register(ENTRY)
