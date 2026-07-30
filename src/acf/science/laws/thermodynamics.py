"""
Atmospheric Thermodynamics Laws
"""

import math
from acf.science.laws.base_law import AtmosphericLaw

THERMODYNAMIC_LAWS = [
    AtmosphericLaw(
        key="first_law_thermodynamics",
        name="Premier Principe de la Thermodynamique",
        domain="Thermodynamique",
        equation="dq = cp * dT - alpha * dp",
        variables={
            "dq": "Chaleur spécifique échangée",
            "cp": "Capacité calorifique à pression constante",
            "dT": "Variation de température",
            "alpha": "Volume massique (1/rho)",
            "dp": "Variation de pression",
        },
        units={"dq": "J/kg", "cp": "J/(kg·K)", "dT": "K", "alpha": "m³/kg", "dp": "Pa"},
        description="Principe de conservation de l'énergie appliqué à une parcelle d'air thermodynamique.",
        references=["WMO Atmospheric Thermodynamics Manual", "Bohren & Albrecht (1998)"],
        limitations=["Processus quasi-statique sans réaction nucléaire."],
    ),
    AtmosphericLaw(
        key="clausius_clapeyron",
        name="Équation de Clausius-Clapeyron",
        domain="Thermodynamique",
        equation="des/dT = (Lv * es) / (Rv * T^2)",
        variables={
            "es": "Pression de vapeur saturante",
            "T": "Température absolue",
            "Lv": "Chaleur latente de vaporisation (2.5e6 J/kg)",
            "Rv": "Constante spécifique de la vapeur d'eau (461.5 J/(kg·K))",
        },
        units={"es": "Pa", "T": "K", "Lv": "J/kg", "Rv": "J/(kg·K)"},
        description="Régit l'augmentation de la pression de vapeur saturante de l'eau en fonction de la température (~7%/K).",
        references=["IPCC AR6 Physical Science Basis", "ECMWF Technical Memoranda"],
        limitations=["Assume une vapeur d'eau se comportant comme un gaz parfait."],
        compute_func=lambda temperature: 611.2 * math.exp((17.67 * (temperature - 273.15)) / (temperature - 29.65)),
    ),
    AtmosphericLaw(
        key="latent_heat_vaporization",
        name="Chaleur Latente de Vaporisation",
        domain="Thermodynamique",
        equation="Lv(T) = 2.501e6 - 2370 * (T - 273.15)",
        variables={"T": "Température absolue", "Lv": "Chaleur latente de vaporisation"},
        units={"T": "K", "Lv": "J/kg"},
        description="Énergie thermique absorbée ou libérée lors du changement de phase eau liquide <-> vapeur.",
        references=["WMO Meteorological Tables", "Rogers & Yau (1989) Cloud Physics"],
        limitations=["Valable pour la plage de températures météorologiques courantes (-40°C à +40°C)."],
        compute_func=lambda temperature: 2.501e6 - 2370.0 * (temperature - 273.15),
    ),
    AtmosphericLaw(
        key="adiabatic_transformation",
        name="Transformation Adiabatique Sèche",
        domain="Thermodynamique",
        equation="T2 = T1 * (p2 / p1) ** (Rd / cp)",
        variables={
            "T1, T2": "Températures initiale et finale",
            "p1, p2": "Pressions initiale et finale",
            "Rd/cp": "Constante Poisson (~0.286)",
        },
        units={"T1, T2": "K", "p1, p2": "Pa"},
        description="Relation entre température et pression lors du déplacement vertical rapide d'une parcelle d'air sec.",
        references=["NOAA Weather Prediction Manual", "Holton & Hakim (2012)"],
        limitations=["Absence d'échange thermique avec l'environnement et absence de condensation."],
        compute_func=lambda t1, p1, p2, kappa=0.286: t1 * (p2 / p1) ** kappa,
    ),
]
