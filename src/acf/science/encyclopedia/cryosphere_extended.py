"""
Cryosphere, Snow Metamorphism, Sea Ice Concentration & Glacier Mass Balance Encyclopedia Module
"""

from acf.science.encyclopedia.cryosphere import calculate_snow_albedo_exponential_decay
from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry


def calculate_sea_ice_growth_rate(
    thermal_conductivity_ice: float, ice_density: float, latent_heat_fusion: float, freezing_temp_c: float, surface_temp_c: float, ice_thickness_m: float
) -> float:
    """
    Croissance de la glace de mer par conduction thermique (loi de
    Stefan) : dh/dt = (k_ice/(rho_ice*Lf)) * (Tf-Tsurface) / h, en m/s.

    NOTE (correction): equation field is fully explicit but this entry
    had no compute_func.
    """
    if ice_thickness_m <= 0.0:
        raise ValueError("ice_thickness_m must be positive.")
    if ice_density <= 0.0:
        raise ValueError("ice_density must be positive.")
    return (thermal_conductivity_ice / (ice_density * latent_heat_fusion)) * (freezing_temp_c - surface_temp_c) / ice_thickness_m


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
        limitations=[
            "Nécessite la prise en compte du dépôt de suie et poussières (effet de neige sale)",
            "Même formule (à renommage de variables près) que cryosphere.py's "
            "'snow_albedo_feedback' - voir la note de calculate_snow_albedo_"
            "exponential_decay() dans ce module partagé.",
        ],
        references=["Brun et al. (1989) J. Glaciol. (Crocus)", "Wiscombe & Warren (1980) J. Atmos. Sci."],
        compute_func=lambda alpha_fresh, alpha_min, k_aging, t: calculate_snow_albedo_exponential_decay(
            alpha_fresh, alpha_min, k_aging, t
        ),
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
        compute_func=calculate_sea_ice_growth_rate,
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
