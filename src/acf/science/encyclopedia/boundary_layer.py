"""
Atmospheric Boundary Layer, Surface Layer, Turbulent Fluxes & Monin-Obukhov Encyclopedia Module
"""

import math
from typing import List
from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

# ---------------------------------------------------------------------------
# Computational Functions for Boundary Layer & Surface Fluxes
# ---------------------------------------------------------------------------

def calculate_obukhov_length(friction_vel_u_star: float, surface_heat_flux_w_theta: float, temp_ref_k: float = 288.15, von_karman: float = 0.4, g: float = 9.81) -> float:
    """Calcul de la longueur d'Obukhov L en mètres."""
    if abs(surface_heat_flux_w_theta) < 1e-6:
        return 1e6 if surface_heat_flux_w_theta >= 0 else -1e6
    return - (friction_vel_u_star ** 3 * temp_ref_k) / (von_karman * g * surface_heat_flux_w_theta)


def calculate_bulk_richardson_number(temp_top: float, temp_bot: float, z_top: float, z_bot: float, u_top: float, v_top: float, u_bot: float = 0.0, v_bot: float = 0.0, g: float = 9.81) -> float:
    """Calcul du Nombre de Richardson Global (Bulk Richardson Number Rib)."""
    dz = z_top - z_bot
    if dz <= 0.0:
        return 0.0
    t_mean = 0.5 * (temp_top + temp_bot)
    du2 = (u_top - u_bot) ** 2 + (v_top - v_bot) ** 2
    if du2 < 1e-4:
        du2 = 1e-4
    return (g / t_mean) * (temp_top - temp_bot) * dz / du2


def calculate_log_wind_profile(u_star: float, z: float, z0: float, von_karman: float = 0.4) -> float:
    """Profil logarithmique du vent en couche limite neutre U(z) = (u_star / kappa) * ln(z / z0)."""
    if z <= z0 or z0 <= 0.0:
        return 0.0
    return (u_star / von_karman) * math.log(z / z0)


# ---------------------------------------------------------------------------
# Encyclopedia Entries
# ---------------------------------------------------------------------------

ENTRIES: List[EncyclopediaEntry] = [
    EncyclopediaEntry(
        key="monin_obukhov_similarity_theory",
        name="Théorie de Similitude de Monin-Obukhov (MOST)",
        domain="Couche Limite Atmosphérique",
        subdomain="Couche de surface",
        equation="dU/dz = (u_star / (kappa * z)) * phi_m(z / L)",
        latex_equation=r"\frac{\partial U}{\partial z} = \frac{u_*}{\kappa z} \phi_m\left(\frac{z}{L}\right)",
        variables={"u_star": "Vitesse de frottement (m/s)", "L": "Longueur d'Obukhov (m)", "phi_m": "Fonction universelle de stabilité de Businger-Dyer"},
        units={"dU/dz": "s⁻¹"},
        description="Formalisme universel régissant les profils verticaux moyens de vent, température et humidité dans la couche de surface en fonction du rapport de stabilité z/L.",
        application_conditions=["Couche de surface constante en flux (10 à 100m au-dessus du sol)"],
        limitations=["Non valide au-dessus du sommet de la couche de surface ou en terrain très complexe"],
        references=["Monin & Obukhov (1954)", "Businger et al. (1971) J. Atmos. Sci.", "Stull (1988)"],
    ),
    EncyclopediaEntry(
        key="obukhov_length_parameter",
        name="Longueur de Stabilité d'Obukhov (L)",
        domain="Couche Limite Atmosphérique",
        subdomain="Couche de surface",
        equation="L = - (u_star^3 * theta0) / (kappa * g * w_theta_surface)",
        latex_equation=r"L = -\frac{u_*^3 \theta_0}{\kappa g \overline{w^\prime \theta^\prime}_0}",
        variables={"u_star": "Vitesse de frottement (m/s)", "w_theta_0": "Flux cinématique de chaleur au sol (K·m/s)"},
        units={"L": "m"},
        description="Échelle de longueur mesurant la hauteur à laquelle la production de TKE par flottabilité dépasse la production par cisaillement dynamique.",
        application_conditions=["Stabilité atmosphérique (L > 0 stable, L < 0 instable, |L| -> inf neutre)"],
        limitations=["Singularité pour flux nul"],
        references=["Obukhov (1946)", "Stull (1988)"],
        compute_func=calculate_obukhov_length,
    ),
    EncyclopediaEntry(
        key="bulk_richardson_number_rib",
        name="Nombre de Richardson Global (Bulk Richardson - Rib)",
        domain="Couche Limite Atmosphérique",
        subdomain="Stabilité de couche limite",
        equation="Rib = (g / T_mean) * (Delta_theta * Delta_z) / ((Delta_u)^2 + (Delta_v)^2)",
        latex_equation=r"Ri_b = \frac{g}{\bar{\theta}} \frac{\Delta \theta \Delta z}{(\Delta U)^2 + (\Delta V)^2}",
        variables={"Delta_theta": "Différence de température potentielle entre 2 niveaux", "Delta_u, Delta_v": "Cisaillement des composantes du vent"},
        units={"Rib": "dimensionless"},
        description="Approximation intégrée du nombre de Richardson utilisée dans les modèles NWP pour déterminer l'épaisseur de la couche limite et le déclenchement du mélange turbulent.",
        application_conditions=["Diagnostics NWP et paramétrisations de couche limite (ex: Mellor-Yamada, Holtslag)"],
        limitations=["Sensible aux épaisseurs des mailles verticales choisies"],
        references=["Holtslag & Boville (1993) J. Climate", "Stull (1988)"],
        compute_func=calculate_bulk_richardson_number,
    ),
    EncyclopediaEntry(
        key="logarithmic_wind_profile",
        name="Profil Logarithmique du Vent",
        domain="Couche Limite Atmosphérique",
        subdomain="Couche de surface",
        equation="U(z) = (u_star / kappa) * ln(z / z0)",
        latex_equation=r"U(z) = \frac{u_*}{\kappa} \ln\left(\frac{z}{z_0}\right)",
        variables={"z0": "Longueur de rugosité de surface (m)", "kappa": "Constante de Von Kármán (~ 0.4)"},
        units={"U": "m/s"},
        description="Profil vertical canonique de la vitesse du vent en condition de stabilité thermique neutre.",
        application_conditions=["Couche de surface neutre (z/L ~ 0)"],
        limitations=["Requiert les fonctions de correction de stabilité de Businger en conditions non-neutres"],
        references=["Prandtl (1925)", "Stull (1988)"],
        compute_func=calculate_log_wind_profile,
    ),
    EncyclopediaEntry(
        key="turbulent_kinetic_energy",
        name="Énergie Cinétique Turbulente (TKE)",
        domain="Couche Limite Atmosphérique",
        subdomain="Turbulence",
        equation="e = 0.5 * (u_prime^2 + v_prime^2 + w_prime^2)",
        latex_equation=r"e = \frac{1}{2}\left(\overline{u^{\prime 2}} + \overline{v^{\prime 2}} + \overline{w^{\prime 2}}\right)",
        variables={"u_prime, v_prime, w_prime": "Fluctuations turbulentes des 3 composantes du vent"},
        units={"e": "m²/s²"},
        description="Mesure de l'intensité moyenne des rumeurs et tourbillons turbulents dans la couche limite.",
        application_conditions=["Couche limite atmosphérique agitée"],
        limitations=["Décomposition de Reynolds requise"],
        references=["Stull (1988) Boundary Layer Meteorology", "ECMWF TKE Parameterization"],
        compute_func=lambda u_var, v_var, w_var: 0.5 * (u_var + v_var + w_var),
    ),
    EncyclopediaEntry(
        key="ekman_spiral",
        name="Spirale d'Ekman en Couche Limite",
        domain="Couche Limite Atmosphérique",
        subdomain="Dynamique de couche limite",
        equation="u(z) = Ug * (1 - exp(-a*z)*cos(a*z)) ; v(z) = Ug * exp(-a*z)*sin(a*z)",
        latex_equation=r"u(z) = U_g \left(1 - e^{-az}\cos az\right), \quad v(z) = U_g e^{-az}\sin az",
        variables={"Ug": "Vent géostrophique au-dessus de la couche limite", "a": "sqrt(f / (2*Km))"},
        units={"u, v": "m/s", "z": "m"},
        description="Rotation progressive et augmentation de l'intensité du vent avec l'altitude sous l'effet du frottement au sol et de Coriolis.",
        application_conditions=["Couche limite laminaire/turbulente stationnaire"],
        limitations=["Viscosité turbulente Km supposée constante"],
        references=["Ekman (1905)", "Stull (1988)"],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
