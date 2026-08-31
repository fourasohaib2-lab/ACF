"""
Precipitation Science, Rain, Snow Crystal Growth & Hail Density Encyclopedia Module
"""

import math

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

# ---------------------------------------------------------------------------
# Computational Functions for Precipitation Physics
# ---------------------------------------------------------------------------


def calculate_marshall_palmer_nd(n0: float, lambda_param: float, diameter_m: float) -> float:
    """Calcul de la distribution en taille des gouttes de pluie N(D) = N0 * exp(-lambda * D)."""
    if diameter_m < 0.0:
        return 0.0
    return n0 * math.exp(-lambda_param * diameter_m)


def calculate_raindrop_terminal_velocity(diameter_m: float) -> float:
    """Calcul de la vitesse limite de chute des gouttes de pluie vt(D) = 9.65 - 10.3 * exp(-600 * D) en m/s."""
    if diameter_m <= 0.0:
        return 0.0
    return max(9.65 - 10.3 * math.exp(-600.0 * diameter_m), 0.0)


def calculate_hailstone_density(wet_growth: bool = True) -> float:
    """Masse volumique typique de la grêle selon le régime de croissance (kg/m³)."""
    return 900.0 if wet_growth else 700.0


# ---------------------------------------------------------------------------
# Encyclopedia Entries
# ---------------------------------------------------------------------------

ENTRIES: list[EncyclopediaEntry] = [
    EncyclopediaEntry(
        key="marshall_palmer_distribution",
        name="Distribution des Tailles de Gouttes de Marshall-Palmer",
        domain="Précipitations",
        subdomain="Microphysique de la pluie",
        equation="N(D) = N0 * exp(-Lambda * D)  (N0 = 8000 m^-3 mm^-1, Lambda = 4.1 * R^-0.21)",
        latex_equation=r"N(D) = N_0 \exp(-\Lambda D), \quad N_0 = 8000 \text{ m}^{-3}\text{mm}^{-1}, \quad \Lambda = 4.1 R^{-0.21} \text{ mm}^{-1}",
        variables={"D": "Diamètre de la goutte (mm)", "R": "Taux de pluie (mm/h)", "N0": "Interception à l'origine"},
        units={"N(D)": "m⁻³·mm⁻¹"},
        description="Distribution exponentielle universelle décrivant le nombre de gouttes de pluie par unité de volume et par intervalle de taille.",
        application_conditions=["Pluies stratiformes stables"],
        limitations=["Sous-estime les très petites gouttes et les très grosses gouttes en pluie convective intense"],
        references=["Marshall & Palmer (1948) J. Meteor.", "WMO Radar Manual"],
        compute_func=calculate_marshall_palmer_nd,
    ),
    EncyclopediaEntry(
        key="terminal_velocity_raindrops",
        name="Vitesse Limite de Chute des Gouttes de Pluie",
        domain="Précipitations",
        subdomain="Chute des hydrométéores",
        equation="vt(D) = 9.65 - 10.3 * exp(-600 * D)",
        latex_equation=r"v_t(D) = 9.65 - 10.3 e^{-600 D}",
        variables={"D": "Diamètre de la goutte de pluie (m)", "vt": "Vitesse limite de chute (m/s)"},
        units={"D": "m", "vt": "m/s"},
        description="Vitesse maximale atteinte par une goutte de pluie lorsque la gravité équilibre la force de traînée aérodynamique.",
        application_conditions=["Précipitations de pluie sous pression atmosphérique standard"],
        limitations=["Valable pour diamètres D entre 0.5 mm et 5.0 mm"],
        references=["Gunn & Kinzer (1949)", "Atlas et al. (1973)"],
        compute_func=calculate_raindrop_terminal_velocity,
    ),
    EncyclopediaEntry(
        key="subcloud_evaporation",
        name="Évaporation Sous-Nuageuse (Virga)",
        domain="Précipitations",
        subdomain="Processus thermodynamiques",
        equation="E_virga = k_evap * (1 - RH) * qr**0.52",
        latex_equation=r"E_{\text{virga}} = k_{\text{evap}} (1 - \text{RH}) q_r^{0.52}",
        variables={"RH": "Humidité relative sous le nuage", "qr": "Contenu en eau de pluie"},
        units={"E_virga": "kg/(kg·s)"},
        description="Évaporation des gouttes de pluie traversant une couche d'air sous-saturée sous la base du nuage, formant parfois des traînées de précipitations n'atteignant pas le sol (virgas).",
        application_conditions=["Couche sous-nuageuse sèche"],
        limitations=["Refroidissement évaporatif puissant déclenchant des rafales descendante (downbursts)"],
        references=["Kessler (1969)", "Rogers & Yau (1989)"],
    ),
    EncyclopediaEntry(
        key="snow_crystal_growth_habits",
        name="Croissance des Cristaux de Neige (Habitus & Dendrites)",
        domain="Précipitations",
        subdomain="Physique de la neige",
        equation="Morphologie = f(Température, Sursaturation par rapport à la glace)",
        latex_equation=r"\text{Habitus}(T) \implies \begin{cases} \text{Plaques/Prismes} & 0^\circ\text{C} > T > -4^\circ\text{C} \\ \text{Aiguilles/Colonnes} & -4^\circ\text{C} \ge T > -10^\circ\text{C} \\ \text{Dendrites stellaires} & -10^\circ\text{C} \ge T > -16^\circ\text{C} \\ \text{Plaques complexes} & -16^\circ\text{C} \ge T > -22^\circ\text{C} \end{cases}",
        variables={"T": "Température de formation de la glace (°C)"},
        units={"Morphologie": "Hexagonale"},
        description="Diagramme de Nakaya répertoriant les formes géométriques de cristaux de neige (dendrites, colonnes, aiguilles, plaques) en fonction de la température et de l'humidité.",
        application_conditions=["Zone de déposition de la glace dans le nuage"],
        limitations=["Les agrégats assemblent des formes multiples lors de la chute"],
        references=["Nakaya (1954) Snow Crystals", "Pruppacher & Klett (1997)"],
    ),
    EncyclopediaEntry(
        key="hailstone_density_growth_modes",
        name="Densité et Modes de Croissance de la Grêle",
        domain="Précipitations",
        subdomain="Physique de la grêle",
        equation="Régime sec (Dry growth: rho ~ 700 kg/m3) vs Régime humide (Wet growth: rho ~ 900 kg/m3)",
        latex_equation=r"\rho_h = \begin{cases} 700\text{--}800 \text{ kg/m}^3 & \text{Croissance sèche (glace opaque)} \\ 900 \text{ kg/m}^3 & \text{Croissance humide (glace transparente)} \end{cases}",
        variables={"rho_h": "Masse volumique du grêlon (kg/m³)"},
        units={"rho_h": "kg/m³"},
        description="Propriétés physiques et masse volumique des grêlons dépendant du bilan thermique de leur surface lors du balayage de gouttelettes surfondues dans le courant ascendant.",
        application_conditions=["Cumulonimbus à fort courant ascendant"],
        limitations=["La densité modifie la vitesse terminale de chute et l'énergie d'impact au sol"],
        references=["Knight & Knight (2001)", "AMS Hail Physics Manual"],
        compute_func=calculate_hailstone_density,
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
