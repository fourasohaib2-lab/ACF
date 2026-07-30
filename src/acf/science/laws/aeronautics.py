"""
Aeronautical Meteorology & Aerodynamics Laws
"""

import math
from acf.science.laws.base_law import AtmosphericLaw

AERONAUTICAL_LAWS = [
    AtmosphericLaw(
        key="isa_temperature_profile",
        name="Modèle Atmosphérique Standard (ISA - Profil de Température)",
        domain="Aéronautique",
        equation="T(z) = T0 - L * z",
        variables={
            "T(z)": "Température ISA à l'altitude z",
            "T0": "Température au niveau de la mer (288.15 K / 15°C)",
            "L": "Gradient thermique vertical standard (0.0065 K/m)",
            "z": "Altitude géopotentielle (m)",
        },
        units={"T": "K", "T0": "K", "L": "K/m", "z": "m"},
        description="Atmosphère normalisée par l’OACI (ICAO Standard Atmosphere Doc 7488) pour le calage altimétrique et la navigation aérienne.",
        references=["ICAO Doc 7488/3 - Manual of the ICAO Standard Atmosphere", "WMO Aeronautical Meteorology Standards"],
        limitations=["Valable dans la troposphère jusqu'à la tropopause standard (11 000 m)."],
        compute_func=lambda altitude_m, T0=288.15, lapse_rate=0.0065: T0 - lapse_rate * altitude_m,
    ),
    AtmosphericLaw(
        key="isa_pressure_profile",
        name="Modèle Atmosphérique Standard (ISA - Profil de Pression)",
        domain="Aéronautique",
        equation="p(z) = p0 * (1 - L*z / T0) ** (g / (R * L))",
        variables={
            "p(z)": "Pression ISA à l'altitude z",
            "p0": "Pression standard niveau de la mer (1013.25 hPa)",
            "L": "Gradient thermique (0.0065 K/m)",
            "g": "Gravité (9.80665 m/s²)",
            "R": "Constante de l'air sec (287.0528 J/(kg·K))",
        },
        units={"p": "hPa", "p0": "hPa", "z": "m"},
        description="Profil de pression atmosphérique standard servant de référence pour les altimètres d'aéronefs (QNH / QNE / FL).",
        references=["ICAO Doc 7488/3", "FAA Instrument Flying Handbook"],
        limitations=["Atmosphère troposphérique neutre sans vent ni humidité."],
        compute_func=lambda altitude_m, p0=1013.25, T0=288.15, L=0.0065, g=9.80665, R=287.0528: (
            p0 * (1.0 - (L * altitude_m) / T0) ** (g / (R * L))
        ),
    ),
    AtmosphericLaw(
        key="speed_of_sound",
        name="Vitesse du Son dans l'Air",
        domain="Aéronautique",
        equation="a = sqrt(gamma * R * T)",
        variables={
            "a": "Vitesse du son dans l'air",
            "gamma": "Indice adiabatique de l'air (~1.40)",
            "R": "Constante de l'air sec (287.05 J/(kg·K))",
            "T": "Température absolue",
        },
        units={"a": "m/s", "gamma": "dimensionless", "R": "J/(kg·K)", "T": "K"},
        description="Vitesse de propagation des ondes de pression acoustiques dans l'air atmosphérique.",
        references=["ICAO Doc 7488/3", "NASA Aerodynamics Handbook"],
        limitations=["Gaz parfait en milieu non réactif."],
        compute_func=lambda temperature, gamma=1.4, R=287.058: math.sqrt(gamma * R * temperature),
    ),
    AtmosphericLaw(
        key="mach_number",
        name="Nombre de Mach",
        domain="Aéronautique",
        equation="M = v / a",
        variables={
            "M": "Nombre de Mach",
            "v": "Vitesse de l'aéronef par rapport à l'air (TAS)",
            "a": "Vitesse locale du son",
        },
        units={"M": "dimensionless", "v": "m/s", "a": "m/s"},
        description="Rapport entre la vitesse de l'aéronef et la vitesse locale du son, régissant les régimes subsoniques, transsoniques et supersoniques.",
        references=["ICAO Aerodynamics Manual", "Anderson, J. D. (2017). Fundamentals of Aerodynamics."],
        limitations=["Présuppose un référentiel lié à la masse d'air."],
        compute_func=lambda speed, speed_of_sound: speed / speed_of_sound,
    ),
    AtmosphericLaw(
        key="reynolds_number",
        name="Nombre de Reynolds",
        domain="Aéronautique",
        equation="Re = (rho * v * L) / mu",
        variables={
            "Re": "Nombre de Reynolds",
            "rho": "Masse volumique de l'air",
            "v": "Vitesse du fluide",
            "L": "Longueur caractéristique (corde d'aile)",
            "mu": "Viscosité dynamique de l'air",
        },
        units={"Re": "dimensionless", "rho": "kg/m³", "v": "m/s", "L": "m", "mu": "Pa·s"},
        description="Rapport entre les forces d'inertie et les forces de viscosité, prédisant le caractère laminaire ou turbulent de l'écoulement.",
        references=["NASA Technical Reports", "Anderson (2017)"],
        limitations=["Écoulement de fluide continu."],
        compute_func=lambda density, velocity, length, dynamic_viscosity=1.789e-5: (
            (density * velocity * length) / dynamic_viscosity
        ),
    ),
    AtmosphericLaw(
        key="aerodynamic_lift",
        name="Équation de la Portance Aérodynamique",
        domain="Aéronautique",
        equation="L = 0.5 * rho * v^2 * S * CL",
        variables={
            "L": "Force de portance",
            "rho": "Masse volumique de l'air",
            "v": "Vitesse vraie par rapport à l'air (TAS)",
            "S": "Surface alaire",
            "CL": "Coefficient de portance",
        },
        units={"L": "N", "rho": "kg/m³", "v": "m/s", "S": "m²", "CL": "dimensionless"},
        description="Force aérodynamique perpendiculaire au vecteur vitesse incidente générée par l'aile en vol.",
        references=["ICAO Flight Performance Manual", "Anderson (2017)"],
        limitations=["Nécessite la connaissance expérimentale ou numérique du coefficient CL."],
        compute_func=lambda density, velocity, surface_area, CL: 0.5 * density * (velocity ** 2) * surface_area * CL,
    ),
    AtmosphericLaw(
        key="aerodynamic_drag",
        name="Équation de la Traînée Aérodynamique",
        domain="Aéronautique",
        equation="D = 0.5 * rho * v^2 * S * CD",
        variables={
            "D": "Force de traînée",
            "rho": "Masse volumique de l'air",
            "v": "Vitesse vraie par rapport à l'air",
            "S": "Surface de référence",
            "CD": "Coefficient de traînée (parasite + induite)",
        },
        units={"D": "N", "rho": "kg/m³", "v": "m/s", "S": "m²", "CD": "dimensionless"},
        description="Force aérodynamique opposée au mouvement de l'aéronef dans l'air.",
        references=["ICAO Performance & Fuel Planning Manual", "Anderson (2017)"],
        limitations=["Dépend fortement de la configuration géométrique de l'appareil."],
        compute_func=lambda density, velocity, surface_area, CD: 0.5 * density * (velocity ** 2) * surface_area * CD,
    ),
]
