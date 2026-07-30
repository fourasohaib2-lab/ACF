"""
Fundamental Physical & Thermodynamic Atmospheric Laws Encyclopedia Module
"""

import math
from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

LAWS = [
    EncyclopediaEntry(
        key="van_der_waals_real_gas",
        name="Loi des Gaz Réels de Van der Waals",
        domain="Physique Atmosphérique",
        subdomain="Thermodynamique des gaz",
        equation="(p + a/V^2) * (V - b) = R * T",
        latex_equation=r"\left(p + \frac{a}{V^2}\right)(V - b) = RT",
        variables={"p": "Pression (Pa)", "V": "Volume molaire (m³/mol)", "a": "Constante d'attraction intermoléculaire", "b": "Covolume des molécules"},
        units={"p": "Pa", "V": "m³/mol"},
        description="Extension de la loi des gaz parfaits prenant en compte le volume propre des molécules et les forces d'attraction intermoléculaires.",
        application_conditions=["Hautes pressions et basses températures"],
        limitations=["Déviations légères pour les fluides supercritiques"],
        references=["Van der Waals (1873)", "Bohren & Albrecht (1998)"],
    ),
    EncyclopediaEntry(
        key="clausius_clapeyron_equation",
        name="Équation de Clausius-Clapeyron",
        domain="Physique Atmosphérique",
        subdomain="Changement de phase de l'eau",
        equation="des/dT = (L_v * es) / (R_v * T^2)",
        latex_equation=r"\frac{de_s}{dT} = \frac{L_v e_s}{R_v T^2}",
        variables={"es": "Pression de vapeur saturante (Pa)", "Lv": "Chaleur latente de vaporisation (2.5e6 J/kg)", "Rv": "Constante des gaz pour la vapeur d'eau (461.5 J/(kg·K))"},
        units={"es": "Pa", "T": "K"},
        description="Relation différentielle fondamentale décrivant l'augmentation exponentielle de la pression de vapeur saturante de l'eau avec la température (~7% par K).",
        application_conditions=["Équilibre liquide-vapeur ou glace-vapeur"],
        limitations=["Lv varie légèrement avec la température"],
        references=["Clausius (1850)", "Clapeyron (1834)", "WMO Technical Note"],
        compute_func=lambda temp_k, es_0=611.2, T0=273.15, Lv=2.5e6, Rv=461.5: es_0 * math.exp((Lv / Rv) * (1.0 / T0 - 1.0 / temp_k)),
    ),
]

for entry in LAWS:
    EncyclopediaRegistry.register(entry)
