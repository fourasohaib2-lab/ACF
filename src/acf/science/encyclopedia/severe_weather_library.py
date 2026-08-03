"""
Severe Weather Encyclopedia Module (Tornadoes, Microbursts, Derechos, Supercells, Atmospheric Rivers)
"""

import math
from typing import List
from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

# ---------------------------------------------------------------------------
# Computational Functions for Severe Weather
# ---------------------------------------------------------------------------

def calculate_ehi_index(cape_j_kg: float, sreh_m2_s2: float) -> float:
    """Calcul de l'indice EHI (Energy Helicity Index) EHI = (CAPE * SREH) / 160000."""
    if cape_j_kg <= 0.0 or sreh_m2_s2 <= 0.0:
        return 0.0
    return (cape_j_kg * sreh_m2_s2) / 160000.0


def calculate_integrated_vapor_transport_ivt(q_kg_kg: float, u_ms: float, v_ms: float, dp_pa: float, g: float = 9.81) -> float:
    """Calcul de l'intensité du transport d'humidité IVT = (1 / g) * q * sqrt(u^2 + v^2) * dp en kg/(m·s)."""
    v_mag = math.sqrt(u_ms**2 + v_ms**2)
    return (1.0 / g) * q_kg_kg * v_mag * dp_pa


# ---------------------------------------------------------------------------
# Encyclopedia Entries
# ---------------------------------------------------------------------------

ENTRIES: List[EncyclopediaEntry] = [
    EncyclopediaEntry(
        key="tornado_ehi_helicity_index",
        name="Tornades, Supercellules et Indice EHI (Energy Helicity Index)",
        domain="Phénomènes Météorologiques Violents",
        subdomain="Tornades & Orages supercellulaires",
        equation="EHI = (CAPE * SREH_0-1km) / 160000  (Échelle EF0 à EF5)",
        latex_equation=r"\text{EHI} = \frac{\text{CAPE} \times \text{SREH}_{0-1\text{km}}}{160000}",
        variables={"CAPE": "Énergie convective disponible (J/kg)", "SREH": "Hélicité relative à la maille (m²/s²)"},
        units={"EHI": "dimensionless"},
        description="Indicateur composé combinant l'instabilité convective et le cisaillement d'hélicité dans les basses couches pour évaluer le potentiel de tornades violentes sous supercellules mesocycloniques.",
        application_conditions=["Diagnostic de prévision des tornades (NOAA Storm Prediction Center SPC)"],
        limitations=["EHI > 2 indique un risque élevé de tornades mesocycloniques EF2+"],
        references=["Rasmussen (2003) Wea. Forecasting", "NOAA SPC Severe Weather Manual"],
        compute_func=calculate_ehi_index,
    ),
    EncyclopediaEntry(
        key="derecho_bow_echo_qlcs",
        name="Derechos, Échos en Arc (Bow Echoes) et QLCS",
        domain="Phénomènes Météorologiques Violents",
        subdomain="Systèmes convectifs de méso-échelle (MCS)",
        equation="Ligne de rafales destructrices continues sur > 400 km avec rafales > 26 m/s (52 kts)",
        latex_equation=r"\text{Derecho} \iff \text{Gusts} > 26\text{ m/s sur } \Delta L > 400\text{ km}",
        variables={"RIJ": "Rear Inflow Jet (Courant d'inflow arrière)", "Path_length": "Longueur de trajectoire > 400 km"},
        units={"Rafales": "m/s"},
        description="Système convectif de méso-échelle ultra-violent générant un couloir ininterrompu de rafales de vent dévastatrices provoquées par l'effondrement du Rear Inflow Jet au niveau du sol.",
        application_conditions=["Grandes plaines nord-américaines et Europe centrale en été"],
        limitations=["Prévision de la trajectoire exacte complexe en raison des interactions de goutte froide"],
        references=["Johns & Hirt (1987) Wea. Forecasting", "Corfidi et al. (2016) AMS Monograph"],
    ),
    EncyclopediaEntry(
        key="atmospheric_river_ivt",
        name="Rivières Atmosphériques et Transport d'Humidité Intégré (IVT)",
        domain="Phénomènes Météorologiques Violents",
        subdomain="Précipitations extrêmes",
        equation="IVT = (1 / g) * int_1000^300 q * V dp  (Seuil IVT > 250 kg/(m*s))",
        latex_equation=r"\mathbf{IVT} = \frac{1}{g} \int_{1000\text{ hPa}}^{300\text{ hPa}} q \mathbf{V} dp",
        variables={"q": "Humidité spécifique (kg/kg)", "V": "Vecteur vent horizontal (m/s)"},
        units={"IVT": "kg/(m·s)"},
        description="Tubes étroits et allongés de transport massif de vapeur d'eau d'origine tropicale traversant les océans et provoquant des pluies torrentielles et des inondations majeures lors de leur impact sur les reliefs côtiers.",
        application_conditions=["Côte Ouest des États-Unis (Pineapple Express), Europe de l'Ouest et Chili"],
        limitations=["IVT > 1000 kg/(m·s) caractérise les rivières atmosphériques de catégorie 5 d'une violence extrême"],
        references=["Zhu & Newell (1998) Mon. Wea. Rev.", "Ralph et al. (2019) Bull. Amer. Meteor. Soc."],
        compute_func=calculate_integrated_vapor_transport_ivt,
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
