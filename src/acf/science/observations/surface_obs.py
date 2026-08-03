"""
WMO Surface Observations Encyclopedia Module (SYNOP, SHIP, BUOY, AWS, Mesonet)
"""

from typing import List
from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

ENTRIES: List[EncyclopediaEntry] = [
    EncyclopediaEntry(
        key="synop_surface_observation",
        name="Observations Surface WMO SYNOP (FM-12 / BUFR TM 307080)",
        domain="Systèmes d'Observation Météorologique",
        subdomain="Surface Terrestre (SYNOP)",
        equation="Réseau Synoptique mondial WMO WIGOS (Horaires 00, 06, 12, 18 UTC)",
        latex_equation=r"\text{SYNOP} \implies (P_{\text{sfc}}, T_{2\text{m}}, T_{d,2\text{m}}, U_{10\text{m}}, V_{10\text{m}}, RR_{24\text{h}}, WW_{\text{present}}, N_{\text{cloud}})",
        variables={"WIGOS_ID": "Identifiant universel WMO WIGOS", "P_sfc": "Pression station / QFF (Pa)", "T2m": "Température sous abri (K)", "Td2m": "Point de rosée (K)", "WW": "Temps présent code WMO 4677"},
        units={"P": "Pa", "T": "K", "Wind": "m/s", "RR": "mm"},
        description="Standard mondial d'observation météorologique en surface produit par les stations synoptiques manuelles et automatiques. Constitue l'épine dorsale de l'assimilation de données de surface dans les modèles NWP.",
        application_conditions=["Assimilation de données NWP (IFS, AROME, GFS, ICON) et climatologie WMO WCDMP"],
        limitations=["Les biais de micro-climat local et d'exposition des abris doivent être corrigés par les modèles d'opérateurs d'observation"],
        references=["WMO-No. 306 Manual on Codes", "WMO-No. 8 Guide to Instruments and Methods of Observation"],
    ),
    EncyclopediaEntry(
        key="ship_buoy_surface_observation",
        name="Observations Maritimes SHIP & Bouées Défrichantes BUOY (WMO FM-13 / FM-18)",
        domain="Systèmes d'Observation Météorologique",
        subdomain="Surface Océanique (SHIP / BUOY)",
        equation="Mesures de surface marine (SST, P_msl, Vent 10m, Vagues H_s)",
        latex_equation=r"\text{BUOY/SHIP} \implies (P_{\text{msl}}, T_{\text{mer}}, T_{\text{air}}, \mathbf{V}_{10\text{m}}, H_s, T_p)",
        variables={"SST": "Sea Surface Temperature (K)", "P_msl": "Pression réduite au niveau de la mer (Pa)", "Hs": "Hauteur significative des vagues (m)"},
        units={"SST": "K", "Hs": "m"},
        description="Observations de surface océanique transmises par les navires de commerce (VOS) et le réseau mondial de bouées ancrées ou dérivantes (DBCP). Vitale pour la prévision des tempêtes marines.",
        application_conditions=["Prévision marine et assimilation NWP/Océan couplée"],
        limitations=["Effet d'ombrage du vent par la superstructure du navire"],
        references=["WMO/IOC DBCP Technical Reports", "WMO-No. 306"],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
