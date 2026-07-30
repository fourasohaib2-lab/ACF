"""
Boundary Layer & Turbulence Laws
"""

import math
from acf.science.laws.base_law import AtmosphericLaw

BOUNDARY_LAYER_LAWS = [
    AtmosphericLaw(
        key="monin_obukhov_length",
        name="Longueur de Monin-Obukhov",
        domain="Couche Limite Atmosphérique",
        equation="L = - (ustar^3 * Tv) / (kappa * g * w_theta_surface)",
        variables={
            "L": "Longueur de Monin-Obukhov",
            "ustar": "Vitesse de frottement",
            "Tv": "Température virtuelle de référence",
            "kappa": "Constante de von Kármán (~0.40)",
            "g": "Accélération de la pesanteur",
            "w_theta_surface": "Flux de chaleur turbulent en surface",
        },
        units={"L": "m", "ustar": "m/s", "Tv": "K", "w_theta_surface": "K·m/s"},
        description="Échelle de longueur caractérisant le rapport entre la production de turbulence thermique (flottabilité) et mécanique (cisaillement).",
        references=["Stull, R. B. (1988). An Introduction to Boundary Layer Meteorology.", "ECMWF IFS PBL Documentation"],
        limitations=["Valable dans la couche de surface atmosphérique stationnaire et homogène."],
    ),
    AtmosphericLaw(
        key="gradient_richardson_number",
        name="Nombre de Richardson Gradient",
        domain="Couche Limite Atmosphérique",
        equation="Ri = (g / theta) * (dtheta/dz) / ((du/dz)^2 + (dv/dz)^2)",
        variables={
            "Ri": "Nombre de Richardson gradient",
            "g": "Gravité",
            "theta": "Température potentielle",
            "dtheta/dz": "Gradient vertical de température potentielle",
            "du/dz, dv/dz": "Cisaillements verticaux du vent",
        },
        units={"Ri": "dimensionless", "g": "m/s²", "theta": "K", "dtheta/dz": "K/m", "shear": "s⁻²"},
        description="Rapport entre la stabilité thermique (flottabilité) et le cisaillement mécanique du vent. Ri < 0.25 indique l'apparition de turbulence.",
        references=["NOAA Boundary Layer Meteorology Manual", "WMO Technical Notes"],
        limitations=["Définition locale aux gradients verticaux infinitésimaux."],
        compute_func=lambda g, theta, dtheta_dz, shear_sq: (g / theta) * dtheta_dz / max(shear_sq, 1e-12),
    ),
    AtmosphericLaw(
        key="bulk_richardson_number",
        name="Nombre de Richardson Bulk",
        domain="Couche Limite Atmosphérique",
        equation="Rib = (g / theta0) * (delta_theta * delta_z) / (delta_u^2 + delta_v^2)",
        variables={
            "Rib": "Nombre de Richardson bulk",
            "delta_theta": "Différence de température potentielle entre 2 niveaux",
            "delta_z": "Épaisseur de la couche",
            "delta_u, delta_v": "Différences de composantes du vent",
        },
        units={"Rib": "dimensionless", "delta_z": "m", "delta_theta": "K", "delta_u, delta_v": "m/s"},
        description="Approximation de Richardson sur une couche d'épaisseur finie (ex: couche limite de surface).",
        references=["ECMWF Boundary Layer Parameterization", "Stull (1988)"],
        limitations=["Sensible au choix des niveaux d'épaisseur delta_z."],
        compute_func=lambda g, theta0, delta_theta, delta_z, delta_wind_sq: (
            (g / theta0) * (delta_theta * delta_z) / max(delta_wind_sq, 1e-12)
        ),
    ),
    AtmosphericLaw(
        key="logarithmic_wind_profile",
        name="Profil Logarithmique du Vent en Couche de Surface",
        domain="Couche Limite Atmosphérique",
        equation="u(z) = (ustar / kappa) * ln(z / z0)",
        variables={
            "u(z)": "Vitesse du vent à l'altitude z",
            "ustar": "Vitesse de frottement",
            "kappa": "Constante de von Kármán (0.40)",
            "z": "Altitude au-dessus du sol",
            "z0": "Longueur de rugosité de surface",
        },
        units={"u(z)": "m/s", "ustar": "m/s", "z": "m", "z0": "m"},
        description="Profil vertical moyen du vent en couche de surface neutre sur sol homogène.",
        references=["WMO Guide to Instruments", "Stull (1988)"],
        limitations=["Valable uniquement en conditions de stabilité neutre (z/L ~ 0)."],
        compute_func=lambda ustar, z, z0, kappa=0.40: (ustar / kappa) * math.log(z / z0),
    ),
]
