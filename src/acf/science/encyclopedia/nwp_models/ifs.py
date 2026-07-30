"""
ECMWF IFS Model Encyclopedia Documentation Module
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

ENTRY = EncyclopediaEntry(
    key="nwp_ecmwf_ifs_specifications",
    name="Spécifications Modèle ECMWF IFS",
    domain="Modèles Numériques NWP",
    subdomain="ECMWF IFS",
    equation="Hydrostatic spectral primitive equations with 4D-Var data assimilation",
    latex_equation=r"\frac{\partial \mathbf{V}}{\partial t} + (\mathbf{V} \cdot \nabla)\mathbf{V} + 2\boldsymbol{\Omega}\times\mathbf{V} = -\frac{1}{\rho}\nabla p + \mathbf{g} + \mathbf{F}",
    description="Modèle spectral global de référence mondiale du CEPMMT (ECMWF).",
    references=["ECMWF IFS Documentation (Cy48r1)", "WMO Technical Reports"],
)

EncyclopediaRegistry.register(ENTRY)
