"""
Atmospheric Radiation Encyclopedia Domain
"""

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

ENTRIES = [
    EncyclopediaEntry(
        key="wien_displacement_law",
        name="Loi du Déplacement de Wien",
        domain="Rayonnement Atmosphérique",
        equation="lambda_max = b / T",
        latex_equation=r"\lambda_{\text{max}} = \frac{b}{T}",
        variables={"b": "Constante de Wien (2.8977719e-3 m·K)", "T": "Température absolue du corps noir (K)"},
        units={"lambda_max": "m", "T": "K"},
        description="Longueur d'onde d'émission maximale d'un corps noir inversement proportionnelle à sa température.",
        application_conditions=["Corps noir en équilibre thermodynamique"],
        limitations=["Emission d'un corps noir parfait"],
        references=["Liou (2002) Atmospheric Radiation", "WMO Guidelines"],
        compute_func=lambda temp_k, b=2.8977719e-3: b / temp_k,
    ),
    EncyclopediaEntry(
        key="rayleigh_scattering_cross_section",
        name="Diffusion de Rayleigh (Molécules d'Air)",
        domain="Rayonnement Atmosphérique",
        equation="sigma_R = (8*pi^3 / 3) * (n^2 - 1)^2 / (N^2 * lambda^4)",
        latex_equation=r"\sigma_R \propto \frac{1}{\lambda^4}",
        variables={"lambda": "Longueur d'onde incident", "n": "Indice de réfraction"},
        units={"sigma_R": "m²"},
        description="Diffusion de la lumière par des particules ou molécules de taille très inférieure à la longueur d'onde (explique le bleu du ciel).",
        application_conditions=["Particules de rayon r << lambda"],
        limitations=["Non valable pour les grosses gouttes ou aérosols (diffusion de Mie)"],
        references=["Rayleigh (1871)", "Liou (2002)"],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
