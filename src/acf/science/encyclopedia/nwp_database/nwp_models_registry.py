"""
Global & Regional NWP Models Database Encyclopedia Module
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

MODELS_DATABASE = [
    {
        "key": "nwp_ukmo_unified_model",
        "name": "UK Met Office Unified Model (UM)",
        "domain": "Modèles Numériques NWP",
        "subdomain": "Modèles globaux et régionaux",
        "equation": "Non-hydrostatic ENDGame dynamical core on rotated lat-lon grid",
        "latex_equation": r"\text{Met Office UM: } 10 \text{ km Global}, \quad 1.5 \text{ km UK}",
        "description": "Système de prévision numérique intégré du Met Office britannique couvrant les échelles globales, régionales et climatiques.",
        "references": ["Wood et al. (2014) Q.J.R. Meteorol. Soc.", "UK Met Office Docs"],
    },
    {
        "key": "nwp_gem_environment_canada",
        "name": "Global Environmental Multiscale Model (GEM - Environment Canada)",
        "domain": "Modèles Numériques NWP",
        "subdomain": "Modèles globaux",
        "equation": "Non-hydrostatic equations on yin-yang grid",
        "latex_equation": r"\Delta x = 15 \text{ km Global}, \quad 2.5 \text{ km Regional}",
        "description": "Modèle opérationnel canadien fondé sur une formulation semi-lagrangienne et semi-implicite.",
        "references": ["Côté et al. (1998) Mon. Wea. Rev.", "Environment Canada Documentation"],
    },
    {
        "key": "nwp_cosmo_consortium",
        "name": "COSMO Model (Consortium for Small-scale Modeling)",
        "domain": "Modèles Numériques NWP",
        "subdomain": "Modèles régionaux",
        "equation": "Non-hydrostatic Euler equations on rotated latitude-longitude grid",
        "latex_equation": r"\Delta x = 2.8 \text{ km} / 1.1 \text{ km}",
        "description": "Modèle méso-échelle européen de haute précision (DWD, MeteoSwiss, ARPAE).",
        "references": ["Baldauf et al. (2011) Mon. Wea. Rev.", "COSMO Consortium Manuals"],
    },
]

for m in MODELS_DATABASE:
    entry = EncyclopediaEntry(
        key=m["key"],
        name=m["name"],
        domain=m["domain"],
        subdomain=m["subdomain"],
        equation=m["equation"],
        latex_equation=m["latex_equation"],
        description=m["description"],
        references=m["references"],
    )
    EncyclopediaRegistry.register(entry)
