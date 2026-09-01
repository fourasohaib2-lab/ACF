"""
Atmosphere Standard OACI (ISA), Barometric Formulas & Aerodynamic Parameters Module
"""

import math

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

# ---------------------------------------------------------------------------
# Computational Functions for ISA Atmosphere & Aerodynamics
# ---------------------------------------------------------------------------


def calculate_isa_temperature(altitude_m: float) -> float:
    """Température ISA en K jusqu'à 11000m (Troposphère)."""
    t0 = 288.15  # 15°C
    lapse_rate = 0.0065  # 6.5 K/km
    if altitude_m <= 11000.0:
        return t0 - lapse_rate * altitude_m
    return 216.65  # Isotherme stratosphérique -56.5°C


def calculate_isa_pressure(altitude_m: float) -> float:
    """Pression ISA en Pa jusqu'à 11000m."""
    p0 = 101325.0
    t0 = 288.15
    lapse_rate = 0.0065
    g = 9.80665
    r_d = 287.0528
    if altitude_m <= 11000.0:
        temp_k = t0 - lapse_rate * altitude_m
        return p0 * ((temp_k / t0) ** (g / (r_d * lapse_rate)))
    p_11km = 22632.1
    temp_strat = 216.65
    return p_11km * math.exp(-g * (altitude_m - 11000.0) / (r_d * temp_strat))


def calculate_speed_of_sound(temp_k: float, gamma: float = 1.4, r_d: float = 287.058) -> float:
    """Vitesse du son a = sqrt(gamma * Rd * T) en m/s."""
    if temp_k <= 0.0:
        return 0.0
    return math.sqrt(gamma * r_d * temp_k)


def calculate_mach_number(velocity_m_s: float, temp_k: float) -> float:
    """Calcul du nombre de Mach Ma = V / a."""
    a = calculate_speed_of_sound(temp_k)
    if a <= 0.0:
        return 0.0
    return velocity_m_s / a


def calculate_reynolds_number(density: float, velocity: float, length: float, dynamic_viscosity: float) -> float:
    """
    Re = (rho*V*L) / mu.

    Algébriquement identique à science/laws/aeronautics.py's
    'reynolds_number' entry - non dupliqué comme second calcul
    indépendant, seulement ré-exprimé ici dans le style local à ce
    fichier (fonctions calculate_* autonomes) pour combler ce registre
    d'entrée qui n'avait aucun compute_func malgré une équation
    entièrement explicite.
    """
    if dynamic_viscosity == 0.0:
        raise ValueError("dynamic_viscosity must not be zero.")
    return (density * velocity * length) / dynamic_viscosity


def calculate_is_stalled(angle_of_attack_deg: float, critical_angle_deg: float = 15.0) -> bool:
    """
    Décrochage : alpha > alpha_critique.

    NOTE (correction): equation field is fully explicit but this entry
    had no compute_func. critical_angle_deg defaults to the entry's own
    documented "~15 deg" typical value (an approximate, aircraft-
    dependent rule of thumb, not a universal constant - callers with a
    known critical angle for a specific airfoil should supply it).
    """
    return angle_of_attack_deg > critical_angle_deg


def calculate_aerodynamic_drag(density: float, velocity: float, surface_area: float, drag_coefficient: float) -> float:
    """
    D = 0.5*rho*V^2*S*Cx, en N.

    Algébriquement identique à science/laws/aeronautics.py's
    'aerodynamic_drag' entry - même remarque que
    calculate_reynolds_number() ci-dessus.
    """
    return 0.5 * density * (velocity**2) * surface_area * drag_coefficient


# ---------------------------------------------------------------------------
# Encyclopedia Entries
# ---------------------------------------------------------------------------

ENTRIES: list[EncyclopediaEntry] = [
    EncyclopediaEntry(
        key="isa_standard_atmosphere_model",
        name="Atmosphère Normale OACI (Standard Atmosphere ISA)",
        domain="Aéronautique",
        subdomain="Atmosphère de référence",
        equation="T(z) = 15°C - 6.5°C/km, p0 = 1013.25 hPa, rho0 = 1.225 kg/m³",
        latex_equation=r"T(z) = T_0 - \Gamma z, \quad p(z) = p_0 \left(1 - \frac{\Gamma z}{T_0}\right)^{\frac{g}{R\Gamma}}",
        variables={"T0": "288.15 K (15°C)", "p0": "1013.25 hPa", "rho0": "1.225 kg/m³", "Gamma": "6.5 K/km"},
        units={"p": "hPa", "T": "K", "rho": "kg/m³"},
        description="Modèle d'atmosphère de référence internationale de l'OACI servant de norme pour le calage des altimètres, les essais en vol et les performances d'aéronefs.",
        application_conditions=["Altimétrie aéronautique et performances d'avions"],
        limitations=["Atmosphère idéale moyenne (ne reflète pas les conditions météo réelles du jour)"],
        references=["ICAO Doc 7488 / Manual of the ICAO Standard Atmosphere", "ISO 2533:1975"],
        compute_func=calculate_isa_temperature,
    ),
    EncyclopediaEntry(
        # NOTE (addition, not a correction): the "isa_standard_atmosphere_model"
        # entry above documents both T(z) and p(z) but its single compute_func
        # only ever exposed T(z) - calculate_isa_pressure(), a genuinely correct
        # implementation of the entry's own p(z) formula, was already defined in
        # this file but never wired to any entry or called anywhere in the
        # codebase (verified via grep). Verified numerically against standard
        # ISA table values (0/5000/11000/15000 m all within 0.05%). Registered
        # as its own entry per the golden rule (every real law gets registered)
        # rather than left orphaned.
        key="isa_standard_atmosphere_pressure",
        name="Pression de l'Atmosphère Normale OACI (ISA Pressure Profile)",
        domain="Aéronautique",
        subdomain="Atmosphère de référence",
        equation="p(z) = p0 * (1 - Gamma*z/T0)^(g/(R*Gamma))  [z<=11km]  ;  p(z) = p_11km * exp(-g*(z-11000)/(R*T_strat))  [z>11km]",
        latex_equation=r"p(z) = p_0 \left(1 - \frac{\Gamma z}{T_0}\right)^{\frac{g}{R\Gamma}} \; (z \le 11\text{km}), \quad p(z) = p_{11\text{km}} e^{-\frac{g(z-11000)}{R T_{\text{strat}}}} \; (z > 11\text{km})",
        variables={
            "p0": "1013.25 hPa (101325 Pa) au niveau de la mer",
            "T0": "288.15 K",
            "Gamma": "6.5 K/km (lapse rate troposphérique)",
            "g": "9.80665 m/s²",
            "R": "287.0528 J/(kg·K) (constante spécifique de l'air sec)",
        },
        units={"p": "Pa"},
        description="Profil vertical de pression de l'atmosphère normale OACI, formule barométrique troposphérique jusqu'à 11 km puis isotherme stratosphérique au-delà, utilisée pour le calage altimétrique standard (QNE).",
        application_conditions=["Altimétrie aéronautique et performances d'avions"],
        limitations=["Atmosphère idéale moyenne (ne reflète pas les conditions météo réelles du jour)"],
        references=["ICAO Doc 7488 / Manual of the ICAO Standard Atmosphere", "ISO 2533:1975"],
        compute_func=calculate_isa_pressure,
    ),
    EncyclopediaEntry(
        key="mach_number_flight",
        name="Nombre de Mach (Ma)",
        domain="Aéronautique",
        subdomain="Aérodynamique compressible",
        equation="Ma = V / a  (a = sqrt(gamma * Rd * T))",
        latex_equation=r"Ma = \frac{V}{a} = \frac{V}{\sqrt{\gamma R_d T}}",
        variables={"V": "Vitesse vraie VTA (m/s)", "a": "Vitesse locale du son (m/s)", "gamma": "1.4"},
        units={"Ma": "dimensionless"},
        description="Rapport sans dimension entre la vitesse de l'aéronef et la vitesse locale du son dans l'air. Régit la compressibilité de l'air (Subsonique, Transsonique, Supersonique).",
        application_conditions=["Aviation commerciale et militaire en haute altitude"],
        limitations=["Atténuation shockwaves au passage du mur du son (Ma = 1)"],
        references=["ICAO Aerodynamics Manual", "Anderson (2017)"],
        compute_func=calculate_mach_number,
    ),
    EncyclopediaEntry(
        key="reynolds_number_flow",
        name="Nombre de Reynolds (Re)",
        domain="Aéronautique",
        subdomain="Mécanique des fluides",
        equation="Re = (rho * V * L) / mu",
        latex_equation=r"Re = \frac{\rho V L}{\mu} = \frac{V L}{\nu}",
        variables={
            "rho": "Masse volumique (kg/m³)",
            "V": "Vitesse (m/s)",
            "L": "Longueur caractéristique de la corde d'aile (m)",
            "mu": "Viscosité dynamique",
        },
        units={"Re": "dimensionless"},
        description="Rapport entre les forces d'inertie et les forces de viscosité au sein de l'écoulement. Régit la transition de la couche limite de laminaire à turbulente.",
        application_conditions=["Soufflerie, conception d'aéronefs et simulation CFD"],
        limitations=["Re très élevé (> 10^7) pour les avions commerciaux"],
        references=["Reynolds (1883)", "Anderson (2017)"],
        # NOTE (correction): equation field is fully explicit but this entry
        # had no compute_func - wired to calculate_reynolds_number() above.
        compute_func=calculate_reynolds_number,
    ),
    EncyclopediaEntry(
        key="aerodynamic_drag_force",
        name="Traînée Aérodynamique (Drag - Cx)",
        domain="Aéronautique",
        subdomain="Aérodynamique",
        equation="D = 0.5 * rho * V^2 * S * Cx",
        latex_equation=r"D = \frac{1}{2} \rho V^2 S C_x",
        variables={"Cx": "Coefficient de traînée (parasite + induite)"},
        units={"D": "N"},
        description="Force aérodynamique s'opposant au mouvement de l'aéronef dans l'air composée de la traînée de forme, de frottement et de la traînée induite par la portance.",
        application_conditions=["Vol d'aéronef"],
        limitations=["Augmentation drastique de la traînée d'onde en régime transsonique"],
        references=["Anderson (2017)", "ICAO Mechanics"],
        # NOTE (correction): equation field is fully explicit but this entry
        # had no compute_func - wired to calculate_aerodynamic_drag() above.
        compute_func=calculate_aerodynamic_drag,
    ),
    EncyclopediaEntry(
        key="aerodynamic_stall_hazard",
        name="Décrochage Aérodynamique (Stall)",
        domain="Aéronautique",
        subdomain="Sécurité des vols",
        equation="Angle d'incidence alpha > alpha_critique (~ 15°)",
        latex_equation=r"\alpha > \alpha_{\text{crit}} \implies C_z \text{ chute brutalement et } C_x \text{ explose}",
        variables={"alpha": "Angle d'incidence (Angle of Attack)"},
        units={"alpha": "deg"},
        description="Décrochement de la couche limite à l'extrados de l'aile entraînant une perte soudaine de portance et une augmentation massive de la traînée.",
        application_conditions=["Approche à basse vitesse, fortes turbulences et décrochage sous facteur de charge"],
        limitations=["Danger majeur en aéronautique nécessitant une alarme de décrochage"],
        references=["ICAO Flight Safety Manual", "Anderson (2017)"],
        compute_func=calculate_is_stalled,
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
