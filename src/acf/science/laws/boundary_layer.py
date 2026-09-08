"""
Boundary Layer & Turbulence Laws
"""

import math

from acf.science.boundary_layer import BowenRatio, FrictionVelocity, MoninObukhovLength, PBLHeight
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
        references=[
            "Stull, R. B. (1988). An Introduction to Boundary Layer Meteorology.",
            "ECMWF IFS PBL Documentation",
        ],
        limitations=["Valable dans la couche de surface atmosphérique stationnaire et homogène."],
        compute_func=lambda friction_velocity, virtual_temperature_k, kinematic_heat_flux: (
            MoninObukhovLength.calculate(friction_velocity, virtual_temperature_k, kinematic_heat_flux)
        ),
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
    AtmosphericLaw(
        key="friction_velocity",
        name="Vitesse de Frottement (u*)",
        domain="Couche Limite Atmosphérique",
        equation="u* = kappa * U(z) / ln(z/z0)",
        variables={
            "U(z)": "Vitesse du vent mesurée à l'altitude z",
            "kappa": "Constante de von Kármán (0.40)",
            "z0": "Longueur de rugosité",
        },
        units={"u*": "m/s", "U(z)": "m/s", "z, z0": "m"},
        description="Inversion du profil logarithmique neutre pour obtenir u* à partir d'une mesure de vent.",
        references=["Stull, R. B. (1988), Ch. 9"],
        limitations=["Valable en conditions de stabilité neutre uniquement."],
        compute_func=lambda wind_speed, height_m, roughness_length_m: (
            FrictionVelocity.calculate(wind_speed, height_m, roughness_length_m)
        ),
    ),
    AtmosphericLaw(
        key="bowen_ratio",
        name="Rapport de Bowen",
        domain="Couche Limite Atmosphérique",
        equation="beta = H/LE = gamma * delta_T / delta_e  ;  gamma = Cp*p / (epsilon*Lv)",
        variables={
            "delta_T": "Différence de température entre 2 niveaux",
            "delta_e": "Différence de pression de vapeur entre les mêmes niveaux",
            "gamma": "Constante psychrométrique",
        },
        units={"beta": "sans dimension", "delta_T": "K", "delta_e": "hPa", "gamma": "hPa/K"},
        description="Méthode du bilan d'énergie de Bowen pour partitionner les flux de chaleur sensible et latente.",
        references=["Bowen, I. S. (1926). Phys. Rev., 27(6), 779-787."],
        limitations=["Suppose des coefficients de transfert turbulent égaux pour chaleur et vapeur d'eau."],
        compute_func=lambda delta_temperature_k, delta_vapor_pressure_hpa, pressure_hpa: (
            BowenRatio.calculate(delta_temperature_k, delta_vapor_pressure_hpa, pressure_hpa)
        ),
    ),
    AtmosphericLaw(
        key="convective_pbl_height_parcel_method",
        name="Hauteur de la Couche Limite Convective (méthode de la parcelle)",
        domain="Couche Limite Atmosphérique",
        equation="Zi : hauteur où theta_env(z) = theta_surface + excess",
        variables={
            "theta_env(z)": "Profil de température potentielle environnementale",
            "theta_surface": "Température potentielle de surface",
            "excess": "Excès superadiabatique (typiquement 0.5-1K)",
        },
        units={"Zi": "m", "theta_env, theta_surface": "K"},
        description="Hauteur à laquelle une thermique sèche partant de la surface devient neutre par rapport à l'environnement.",
        references=["Holzworth, G. C. (1964). Mon. Wea. Rev., 92(5), 235-242."],
        limitations=["Ne s'applique qu'à la couche limite convective diurne (pas la couche limite stable nocturne)."],
        compute_func=lambda height_profile_m, potential_temperature_profile_k, surface_potential_temperature_k, excess_k=0.0: (
            PBLHeight.parcel_method(
                height_profile_m, potential_temperature_profile_k, surface_potential_temperature_k, excess_k
            )
        ),
    ),
]
