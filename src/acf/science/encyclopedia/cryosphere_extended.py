"""
Cryosphere, Snow Metamorphism, Sea Ice Concentration & Glacier Mass Balance Encyclopedia Module
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

ENTRIES: list[EncyclopediaEntry] = [
    EncyclopediaEntry(
        key="snow_albedo_aging_metamorphism",
        name="Métamorphose de la Neige et Décroissance de l'Albédo",
        domain="Cryosphère",
        subdomain="Physique de la neige",
        equation="Albédo de la neige alpha_snow(t) = alpha_min + (alpha_fresh - alpha_min) * exp(-k_aging * t)",
        latex_equation=r"\alpha_{\text{snow}}(t) = \alpha_{\text{min}} + (\alpha_{\text{fraîche}} - \alpha_{\text{min}}) e^{-k_{\text{aging}} t}",
        variables={
            "alpha_fresh": "Albédo neige fraîche (~ 0.85)",
            "alpha_min": "Albédo neige ancienne mouillée (~ 0.50)",
            "k_aging": "Taux de vieillissement",
        },
        units={"albedo": "dimensionless"},
        description="Processus physique de transformation des grains de neige sous l'effet des gradients de température et du regel, entraînant une diminution progressive du pouvoir réfléchissant radiatif de la couche de neige.",
        application_conditions=[
            "Modèles de manteau neigeux (Crocus, SURFEX/ISBA-ES, Noah-MP) et prévision des avalanches"
        ],
        limitations=["Nécessite la prise en compte du dépôt de suie et poussières (effet de neige sale)"],
        references=["Brun et al. (1989) J. Glaciol. (Crocus)", "Wiscombe & Warren (1980) J. Atmos. Sci."],
    ),
    EncyclopediaEntry(
        key="sea_ice_thermodynamics_cice",
        name="Thermodynamique de la Glace de Mer (CICE / GELATO)",
        domain="Cryosphère",
        subdomain="Glace de mer & Océan polaire",
        equation="Croissance de la glace par conduction thermique: dh/dt = (k_ice / (rho_ice * L_f)) * (T_f - T_surface) / h",
        latex_equation=r"\frac{dh}{dt} = \frac{k_{\text{ice}}}{\rho_{\text{ice}} L_f} \frac{T_f - T_{\text{surface}}}{h}",
        variables={
            "h": "Épaisseur de la glace de mer (m)",
            "k_ice": "Conductivité thermique de la glace (2.0 W/(m·K))",
            "Lf": "Chaleur latente de fusion (3.34e5 J/kg)",
        },
        units={"h": "m"},
        description="Loi thermodynamique régissant la croissance en épaisseur de la glace de mer par congélation au contact de l'eau de mer polaire en hiver et sa fonte estivale.",
        application_conditions=["Modèles de glace de mer couplés océan-atmosphère (CICE, NEMO-LIM, GELATO)"],
        limitations=["Nécessite le suivi de la salinité des saumures incluses dans la glace"],
        references=["Untersteiner (1965) J. Geophys. Res.", "Hunke & Lipscomb (2008) CICE Documentation"],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
