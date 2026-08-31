"""
Clouds & Cloud Microphysics Encyclopedia Domain
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

ENTRIES = [
    EncyclopediaEntry(
        key="wmo_cloud_classification",
        name="Classification Officielle des Nuages (OMM)",
        domain="Nuages & Microphysique",
        subdomain="Morphologie & Nébulosité",
        equation="Classification by Height (High, Mid, Low) and Vertical Convection",
        latex_equation=r"\text{Genres OMM} \in \{\text{Ci, Cs, Cc, As, Ac, St, Sc, Ns, Cu, Cb}\}",
        variables={"Altitude": "Base et sommet (m)", "Température": "Structure thermique (°C)"},
        units={"Altitude": "m"},
        description="Classification internationale en 10 genres nuageux (WMO International Cloud Atlas).",
        application_conditions=["Observations météorologiques de surface et télédétection"],
        limitations=["Subjectivité visuelle en observation humaine compensée par algorithmes radars/satellites"],
        references=["WMO International Cloud Atlas (2017)", "ICAO Annex 3"],
    ),
    EncyclopediaEntry(
        # NOTE (correction - registry key collision, this one
        # consequential): this used to be registered as
        # "thompson_microphysics_scheme", the SAME key as
        # parameterizations/operational_schemes.py's more detailed
        # aerosol-aware Thompson entry - which has NO compute_func
        # (descriptive-only). Depending on unrelated import order, this
        # entry's working compute_func (qc+qr+qi+qs+qg total condensed
        # water) was silently replaced by the other's None, meaning
        # EncyclopediaRegistry.calculate("thompson_microphysics_scheme", ...)
        # could non-deterministically fail with NotImplementedError even
        # though a working implementation existed. Renamed so this
        # working entry is always independently accessible. See
        # EncyclopediaRegistry.register()'s collision guard.
        key="thompson_microphysics_scheme_basic",
        name="Schéma Microphysique de Thompson",
        domain="Nuages & Microphysique",
        subdomain="Paramétrisation microphysique des modèles NWP",
        equation="Prognostic variables: qc, qr, qi, qs, qg, Ni, Nr",
        latex_equation=r"\frac{\partial \rho q_x}{\partial t} + \nabla \cdot (\rho q_x \mathbf{V}) = S_x",
        variables={"qc, qr, qi, qs, qg": "Rapports de mélange des 5 espèces d'eau/glace"},
        units={"q": "kg/kg"},
        description="Schéma microphysique à 2 moments très utilisé dans WRF et MPAS pour la prévision des précipitations et de la neige.",
        references=["Thompson et al. (2008) Mon. Wea. Rev.", "NCAR WRF Technical Manual"],
        compute_func=lambda qc, qr, qi, qs, qg: qc + qr + qi + qs + qg,
    ),
    EncyclopediaEntry(
        key="lin_microphysics_scheme",
        name="Schéma Microphysique de Lin et al.",
        domain="Nuages & Microphysique",
        subdomain="Paramétrisation microphysique",
        equation="Bulk 5-class microphysics scheme (qc, qr, qi, qs, qg)",
        latex_equation=r"S_{lin} = P_{auto} + P_{accre} + P_{melt} + P_{subl}",
        variables={"qc, qr, qi, qs, qg": "Espèces hydrométéores"},
        units={"q": "kg/kg"},
        description="Schéma pionnier à 5 classes développé pour la modélisation convective à haute résolution.",
        references=["Lin, Farley & Orville (1983) J. Climate Appl. Meteor."],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
