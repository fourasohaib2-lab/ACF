"""
Atmospheric Radiation, Radiative Transfer, Planck, Stefan-Boltzmann & Satellite Applications Encyclopedia Module
"""

import math
from typing import List
from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

# ---------------------------------------------------------------------------
# Computational Functions for Radiation
# ---------------------------------------------------------------------------

def calculate_planck_radiance(wavelength_m: float, temp_k: float) -> float:
    """Calcul de la luminance de corps noir Planck B_lambda(T) en W/(m²·sr·m)."""
    h = 6.62607015e-34  # Planck constant
    c = 2.99792458e8   # Speed of light
    k_b = 1.380649e-23  # Boltzmann constant

    if wavelength_m <= 0.0 or temp_k <= 0.0:
        return 0.0

    c1 = 2.0 * h * (c ** 2)
    c2 = (h * c) / (k_b * temp_k)
    exponent = c2 / wavelength_m
    if exponent > 700.0:
        return 0.0
    return c1 / ((wavelength_m ** 5) * (math.exp(exponent) - 1.0))


def calculate_stefan_boltzmann_flux(temp_k: float, emissivity: float = 1.0) -> float:
    """Calcul de la puissance surfacique émise E = emissivity * sigma * T^4 en W/m²."""
    sigma = 5.670374419e-8  # Stefan-Boltzmann constant
    return emissivity * sigma * (temp_k ** 4)


def calculate_beer_lambert_attenuation(i0: float, optical_depth_tau: float) -> float:
    """Calcul de l'intensité transmise I = I0 * exp(-tau)."""
    return i0 * math.exp(-optical_depth_tau)


# ---------------------------------------------------------------------------
# Encyclopedia Entries
# ---------------------------------------------------------------------------

ENTRIES: List[EncyclopediaEntry] = [
    EncyclopediaEntry(
        key="planck_blackbody_law",
        name="Loi de Planck du Rayonnement de Corps Noir",
        domain="Rayonnement Atmosphérique",
        subdomain="Émission thermique",
        equation="B_lambda(T) = (2*h*c^2 / lambda^5) / (exp(h*c / (lambda*k_B*T)) - 1)",
        latex_equation=r"B_\lambda(T) = \frac{2 h c^2}{\lambda^5} \frac{1}{\exp\left(\frac{h c}{\lambda k_B T}\right) - 1}",
        variables={"h": "Constante de Planck (6.626e-34 J·s)", "c": "Vitesse de la lumière (3e8 m/s)", "kB": "Constante de Boltzmann (1.38e-23 J/K)", "lambda": "Longueur d'onde (m)"},
        units={"B_lambda": "W/(m²·sr·m)"},
        description="Loi fondamentale décrivant la distribution spectrale de l'énergie électromagnétique émise par un corps noir à la température T.",
        application_conditions=["Corps noir à l'équilibre thermodynamique local"],
        limitations=["Les surfaces réelles ont une émissivité spectrale epsilon_lambda < 1"],
        references=["Planck (1900)", "Liou (2002) Atmospheric Radiation"],
        compute_func=calculate_planck_radiance,
    ),
    EncyclopediaEntry(
        key="wien_displacement_law",
        name="Loi du Déplacement de Wien",
        domain="Rayonnement Atmosphérique",
        subdomain="Émission thermique",
        equation="lambda_max = b / T",
        latex_equation=r"\lambda_{\text{max}} = \frac{b}{T}",
        variables={"b": "Constante de Wien (2.8977719e-3 m·K)", "T": "Température absolue du corps noir (K)"},
        units={"lambda_max": "m", "T": "K"},
        description="Longueur d'onde d'émission maximale d'un corps noir inversement proportionnelle à sa température. Explique la séparation entre rayonnement solaire court (0.5 µm) et thermique terrestre long (10 µm).",
        application_conditions=["Corps noir en équilibre thermodynamique"],
        limitations=["Émission d'un corps noir parfait"],
        references=["Wien (1893)", "Liou (2002)"],
        compute_func=lambda temp_k, b=2.8977719e-3: b / temp_k,
    ),
    EncyclopediaEntry(
        key="stefan_boltzmann_law",
        name="Loi de Stefan-Boltzmann",
        domain="Rayonnement Atmosphérique",
        subdomain="Émission thermique",
        equation="E = emissivity * sigma * T^4",
        latex_equation=r"E = \epsilon \sigma T^4",
        variables={"sigma": "Constante de Stefan-Boltzmann (5.670374e-8 W/(m²·K⁴))", "emissivity": "Émissivité de la surface"},
        units={"E": "W/m²"},
        description="Loi décrivant l'émittance totale intégrée sur toutes les longueurs d'onde d'un corps noir à la température T.",
        application_conditions=["Intégration spectrale complète de 0 à l'infini"],
        limitations=["Requiert une émissivité moyenne pondérée pour les corps gris"],
        references=["Stefan (1879)", "Boltzmann (1884)", "Liou (2002)"],
        compute_func=calculate_stefan_boltzmann_flux,
    ),
    EncyclopediaEntry(
        key="beer_lambert_law",
        name="Loi de Beer-Lambert-Bouguer",
        domain="Rayonnement Atmosphérique",
        subdomain="Extinction & Absorption",
        equation="I(lambda) = I0(lambda) * exp(-tau_lambda)",
        latex_equation=r"I_\lambda(s) = I_{\lambda,0} \exp\left(-\tau_\lambda\right) = I_{\lambda,0} \exp\left(-\int k_\lambda \rho \, ds\right)",
        variables={"tau_lambda": "Épaisseur optique spectrale intégrée", "k_lambda": "Coefficient d'extinction massique"},
        units={"I": "W/(m²·sr·µm)"},
        description="Loi décrivant l'atténuation exponentielle d'un faisceau lumineux traversant un milieu absorbant et diffusant.",
        application_conditions=["Propagation en ligne droite sans sources d'émission internes"],
        limitations=["Ne prend pas en compte la diffusion multiple"],
        references=["Beer (1852)", "Lambert (1760)", "Liou (2002)"],
        compute_func=calculate_beer_lambert_attenuation,
    ),
    EncyclopediaEntry(
        key="rayleigh_scattering_cross_section",
        name="Diffusion de Rayleigh (Molécules d'Air)",
        domain="Rayonnement Atmosphérique",
        subdomain="Diffusion",
        equation="sigma_R = (8*pi^3 / 3) * (n^2 - 1)^2 / (N^2 * lambda^4)",
        latex_equation=r"\sigma_R \propto \frac{1}{\lambda^4}",
        variables={"lambda": "Longueur d'onde incidente", "n": "Indice de réfraction de l'air"},
        units={"sigma_R": "m²"},
        description="Diffusion de la lumière par des particules ou molécules de taille très inférieure à la longueur d'onde (r << lambda). Explique la couleur bleue du ciel et la polarisation du ciel clair.",
        application_conditions=["Particules de rayon r < 0.1 * lambda"],
        limitations=["Non valable pour les grosses gouttes de nuage ou aérosols (diffusion de Mie)"],
        references=["Rayleigh (1871)", "Liou (2002)"],
    ),
    EncyclopediaEntry(
        key="radiative_transfer_equation",
        name="Équation du Transfert Radiatif (RTE)",
        domain="Rayonnement Atmosphérique",
        subdomain="Transfert radiatif",
        equation="dI_lambda / dtau = - I_lambda + J_lambda",
        latex_equation=r"\mu \frac{d I_\lambda}{d \tau_\lambda} = -I_\lambda(\tau_\lambda, \mu, \phi) + J_\lambda(\tau_\lambda, \mu, \phi)",
        variables={"J_lambda": "Fonction source spectrale (émission + diffusion multiple)", "mu": "cos(zenith_angle)"},
        units={"I": "W/(m²·sr·µm)"},
        description="Équation intégro-différentielle gouvernant la propagation, l'extinction, l'émission thermique et la diffusion de l'énergie rayonnante dans l'atmosphère.",
        application_conditions=["Modèles radiatifs NWP (ex: RRTMG, ECMWF EcRad) et restitution satellitaire (RTTOV)"],
        limitations=["Résolution numérique coûteuse nécessitant des approximations à 2 flux (two-stream approximation)"],
        references=["Chandrasekhar (1960) Radiative Transfer", "Liou (2002)", "ECMWF EcRad Documentation"],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
