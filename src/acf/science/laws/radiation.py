"""
Radiative Transfer & Solar/Terrestrial Radiation Laws
"""

import math
from acf.science.laws.base_law import AtmosphericLaw

RADIATION_LAWS = [
    AtmosphericLaw(
        key="stefan_boltzmann",
        name="Loi de Stefan-Boltzmann",
        domain="Rayonnement Atmosphérique",
        equation="E = sigma * T^4",
        variables={
            "E": "Émittance énergétique totale du corps noir",
            "sigma": "Constante de Stefan-Boltzmann (5.670374e-8 W/(m²·K⁴))",
            "T": "Température absolue du corps",
        },
        units={"E": "W/m²", "sigma": "W/(m²·K⁴)", "T": "K"},
        description="Puissance totale rayonnée par unité de surface d'un corps noir en fonction de sa température.",
        references=["WMO Radiation & Remote Sensing Guide", "Liou, K. N. (2002). An Introduction to Atmospheric Radiation."],
        limitations=["Corps noir idéal en équilibre thermodynamique local."],
        compute_func=lambda temperature, sigma=5.670374e-8: sigma * (temperature ** 4),
    ),
    AtmosphericLaw(
        key="beer_lambert",
        name="Loi de Beer-Lambert (Extinction Radiative)",
        domain="Rayonnement Atmosphérique",
        equation="I = I0 * exp(-tau)",
        variables={
            "I": "Intensité transmise",
            "I0": "Intensité incidente",
            "tau": "Épaisseur optique du milieu traversé",
        },
        units={"I, I0": "W/(m²·sr)", "tau": "dimensionless"},
        description="Atténuation de l'intensité d'un faisceau lumineux traversant un milieu absorbant et diffusant.",
        references=["NASA Earth Observatory Satellite Calibration Docs", "Liou (2002)"],
        limitations=["Absence de diffusion multiple et d'émission propre le long du trajet."],
        compute_func=lambda I0, optical_depth: I0 * math.exp(-optical_depth),
    ),
    AtmosphericLaw(
        key="planck_law",
        name="Loi de Planck (Luminance Monochromatique)",
        domain="Rayonnement Atmosphérique",
        equation="B_lambda(T) = (2*h*c^2 / lambda^5) / (exp(h*c / (lambda*k*T)) - 1)",
        variables={
            "B_lambda": "Luminance spectrale du corps noir",
            "lambda": "Longueur d'onde",
            "T": "Température absolue",
            "h": "Constante de Planck (6.62607e-34 J·s)",
            "c": "Vitesse de la lumière (2.99792e8 m/s)",
            "k": "Constante de Boltzmann (1.380649e-23 J/K)",
        },
        units={"B_lambda": "W/(m²·sr·m)", "lambda": "m", "T": "K"},
        description="Distribution spectrale de l'énergie émise par un corps noir à une température donnée.",
        references=["Liou (2002)", "WMO Satellite Meteorology Manual"],
        limitations=["Équilibre thermodynamique local."],
    ),
]
