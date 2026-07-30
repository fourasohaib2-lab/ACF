"""
NWP Cloud Microphysics Schemes Encyclopedia Module
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

SCHEMES = [
    {
        "key": "arome_ice3_scheme",
        "name": "Schéma Microphysique ICE3 (Météo-France / AROME)",
        "domain=": "Nuages & Microphysique",
        "subdomain": "Schémas NWP",
        "equation": "Prognostic: qc, qr, qi, qs, qg (5 hydrométéores)",
        "latex_equation": r"\frac{\partial (\rho q_x)}{\partial t} = \text{ADV} + \text{DIF} + S_{ICE3}",
        "description": "Schéma microphysique à 1 moment utilisé opérationnellement dans AROME pour modéliser les nuages et précipitations à haute résolution.",
        "references": ["Pinty & Jabouille (1998)", "Météo-France AROME Documentation"],
    },
    {
        "key": "arome_ice4_scheme",
        "name": "Schéma Microphysique ICE4 (Météo-France / Meso-NH)",
        "domain=": "Nuages & Microphysique",
        "subdomain": "Schémas NWP",
        "equation": "Prognostic: qc, qr, qi, qs, qg, qh (6 hydrométéores avec grêle explicitée)",
        "latex_equation": r"\frac{\partial (\rho q_h)}{\partial t} = S_{hail\_riming} + S_{hail\_wet\_growth}",
        "description": "Extension à 6 espèces d'ICE3 incluant la grêle explicite (qh) pour les orages violents.",
        "references": ["Lascaux et al. (2006)", "Meso-NH Scientific Manual"],
    },
    {
        "key": "icon_seifert_beheng",
        "name": "Schéma à 2 Moments Seifert-Beheng (DWD / ICON)",
        "domain=": "Nuages & Microphysique",
        "subdomain": "Schémas NWP",
        "equation": "Prognostic: q_x and N_x for all 6 hydrometeor species",
        "latex_equation": r"\frac{\partial N_x}{\partial t} = S_{N,x}, \quad \frac{\partial q_x}{\partial t} = S_{q,x}",
        "description": "Schéma à 2 moments prédisant simultanément les rapports de mélange et les concentrations numériques des gouttelettes et de la glace.",
        "references": ["Seifert & Beheng (2006) Meteor. Atmos. Phys.", "DWD ICON Manual"],
    },
    {
        "key": "wrf_morrison_scheme",
        "name": "Schéma Microphysique de Morrison à 2 Moments (WRF)",
        "domain=": "Nuages & Microphysique",
        "subdomain": "Schémas NWP",
        "equation": "2-moment scheme for liquid and ice hydrometeor numbers and mass",
        "latex_equation": r"N(D) = N_0 D^\mu e^{-\lambda D}",
        "description": "Schéma microphysique avancé prédisant les moments 0 et 3 des distributions en taille d'hydrométéores.",
        "references": ["Morrison et al. (2009) Mon. Wea. Rev.", "NCAR WRF Technical Note"],
    },
]

for s in SCHEMES:
    entry = EncyclopediaEntry(
        key=s["key"],
        name=s["name"],
        domain="Nuages & Microphysique",
        subdomain=s["subdomain"],
        equation=s["equation"],
        latex_equation=s["latex_equation"],
        description=s["description"],
        references=s["references"],
    )
    EncyclopediaRegistry.register(entry)
