"""
Surface Hydrology, Infiltration, River Routing & Watershed Dynamics Encyclopedia Module
"""

import math
from typing import List
from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

# ---------------------------------------------------------------------------
# Computational Functions for Hydrology
# ---------------------------------------------------------------------------

def calculate_horton_infiltration(f0: float, fc: float, k: float, time_hours: float) -> float:
    """Calcul du taux d'infiltration selon le modèle de Horton f(t) = fc + (f0 - fc) * exp(-k * t) en mm/h."""
    if time_hours < 0.0:
        return f0
    return fc + (f0 - fc) * math.exp(-k * time_hours)


def calculate_rational_peak_runoff(c: float, i_mm_h: float, area_km2: float) -> float:
    """Calcul du débit de pointe par la méthode rationnelle Q = (C * I * A) / 3.6 en m³/s."""
    if i_mm_h < 0.0 or area_km2 < 0.0:
        return 0.0
    return (c * i_mm_h * area_km2) / 3.6


def calculate_muskingum_routing_coefficients(dt_hours: float, k_hours: float, x: float) -> tuple:
    """Calcul des coefficients C0, C1, C2 de l'équation de Muskingum."""
    denom = 2.0 * k_hours * (1.0 - x) + dt_hours
    if denom == 0.0:
        return (0.0, 0.0, 0.0)
    c0 = (-2.0 * k_hours * x + dt_hours) / denom
    c1 = (2.0 * k_hours * x + dt_hours) / denom
    c2 = (2.0 * k_hours * (1.0 - x) - dt_hours) / denom
    return (c0, c1, c2)


# ---------------------------------------------------------------------------
# Encyclopedia Entries
# ---------------------------------------------------------------------------

ENTRIES: List[EncyclopediaEntry] = [
    EncyclopediaEntry(
        key="green_ampt_infiltration_model",
        name="Modèle d'Infiltration de Green-Ampt",
        domain="Hydrologie Atmosphérique",
        subdomain="Hydrologie de surface",
        equation="f(t) = Ks * (1 + (psi * Delta_theta) / F(t))",
        latex_equation=r"f(t) = K_s \left(1 + \frac{\psi \Delta \theta}{F(t)}\right)",
        variables={"Ks": "Conductivité hydraulique à saturation (mm/h)", "psi": "Succion au front d'humectation (mm)", "Delta_theta": "Déficit en eau du sol", "F(t)": "Infiltration cumulée (mm)"},
        units={"f": "mm/h", "Ks": "mm/h", "F": "mm"},
        description="Modèle physique basé sur la loi de Darcy décrivant l'infiltration de l'eau de pluie dans un sol non saturé avec un front d'humectation net.",
        application_conditions=["Sols homogènes avec nappe phréatique profonde et pluie continue"],
        limitations=["Suppose un profil de teneur en eau rectangulaire simplifié au niveau du front"],
        references=["Green & Ampt (1911) J. Agric. Sci.", "WMO Hydrological Manual", "Chow et al. (1988) Applied Hydrology"],
    ),
    EncyclopediaEntry(
        key="horton_infiltration_law",
        name="Équation d'Infiltration de Horton",
        domain="Hydrologie Atmosphérique",
        subdomain="Hydrologie de surface",
        equation="f(t) = fc + (f0 - fc) * exp(-k * t)",
        latex_equation=r"f(t) = f_c + (f_0 - f_c) e^{-k t}",
        variables={"f0": "Taux d'infiltration initial (mm/h)", "fc": "Taux d'infiltration d'équilibre (mm/h)", "k": "Constante de décroissance (h⁻¹)"},
        units={"f": "mm/h", "k": "h⁻¹"},
        description="Formulation empirique classique décrivant la baisse exponentielle de la capacité d'infiltration du sol au fur et à mesure de sa saturation par la pluie.",
        application_conditions=["Modélisation des crues et ruissellement de surface"],
        limitations=["Empirique, les paramètres f0 et k dépendent fortement du type de sol et du couvert végétal"],
        references=["Horton (1939) Soil Sci. Soc. Am. Proc.", "WMO Guide to Hydrological Practices"],
        compute_func=calculate_horton_infiltration,
    ),
    EncyclopediaEntry(
        key="richards_equation_soil_moisture",
        name="Équation de Richards pour la Teneur en Eau du Sol",
        domain="Hydrologie Atmosphérique",
        subdomain="Physique du sol",
        equation="d(theta)/dt = d/dz [ K(theta) * (d(psi)/dz + 1) ]",
        latex_equation=r"\frac{\partial \theta}{\partial t} = \frac{\partial}{\partial z} \left[ K(\theta) \left( \frac{\partial \psi}{\partial z} + 1 \right) \right]",
        variables={"theta": "Humidité volumique du sol (m³/m³)", "psi": "Pression matricielle du sol (m)", "K(theta)": "Conductivité hydraulique (m/s)"},
        units={"theta": "m³/m³", "K": "m/s"},
        description="Équation aux dérivées partielles fondamentale décrivant le mouvement non saturé de l'eau dans le sol sous l'effet conjugué des forces capillaires et de la gravité.",
        application_conditions=["Couche de sol non saturée dans les modèles de surface (Land Surface Models ex: SURFEX, Noah-MP)"],
        limitations=["Fortement non-linéaire nécessitant des schémas d'intégration numériques implicites (van Genuchten / Clapp-Hornberger)"],
        references=["Richards (1931) Physics", "Clapp & Hornberger (1978) Water Resour. Res."],
    ),
    EncyclopediaEntry(
        key="muskingum_river_routing",
        name="Méthode de Propagation de Crue de Muskingum",
        domain="Hydrologie Atmosphérique",
        subdomain="Hydrologie fluviale",
        equation="Q_(t+1) = C0 * I_(t+1) + C1 * I_t + C2 * Q_t",
        latex_equation=r"Q_{t+1} = C_0 I_{t+1} + C_1 I_t + C_2 Q_t",
        variables={"I": "Débit d'entrée en amont (m³/s)", "Q": "Débit de sortie en aval (m³/s)", "K": "Temps de transit dans le bief (h)", "X": "Facteur de pondération de stockage (0 à 0.5)"},
        units={"Q": "m³/s", "I": "m³/s"},
        description="Méthode de calcul de propagation d'onde de crue le long d'un réseau hydrographique basée sur l'équation de continuité et une relation de stockage prisme-coin.",
        application_conditions=["Écoulements en rivières et prévision des crues"],
        limitations=["Ne prend pas en compte les effets de remous aval forts (backwater effects)"],
        references=["McCarthy (1938)", "WMO Operational Hydrology Manual"],
        compute_func=calculate_muskingum_routing_coefficients,
    ),
    EncyclopediaEntry(
        key="rational_method_peak_flow",
        name="Méthode Rationnelle du Débit de Pointe de Ruissellement",
        domain="Hydrologie Atmosphérique",
        subdomain="Hydrologie de bassin versant",
        equation="Q_p = (C * I * A) / 3.6",
        latex_equation=r"Q_p = \frac{C \cdot I \cdot A}{3.6}",
        variables={"C": "Coefficient de ruissellement (0 à 1)", "I": "Intensité de pluie moyenne pendant le temps de concentration (mm/h)", "A": "Superficie du bassin versant (km²)"},
        units={"Qp": "m³/s", "I": "mm/h", "A": "km²"},
        description="Formule empirique standard pour estimer le débit maximal de ruissellement lors d'un épisode pluvieux sur un petit bassin versant.",
        application_conditions=["Petits bassins versants urbains ou ruraux (A < 25 km²)"],
        limitations=["Suppose une pluie uniforme et constante pendant une durée égale au temps de concentration"],
        references=["Mulvany (1851)", "WMO Hydrological Guide"],
        compute_func=calculate_rational_peak_runoff,
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
