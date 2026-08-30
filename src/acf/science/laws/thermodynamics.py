"""
Atmospheric Thermodynamics Laws
"""

import math

from acf.science.cape import CAPE
from acf.science.cin import CIN
from acf.science.equivalent_potential_temperature import EquivalentPotentialTemperature
from acf.science.laws.base_law import AtmosphericLaw
from acf.science.lcl import LCL

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
        compute_func=lambda cp, dT, alpha, dp: cp * dT - alpha * dp,
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
    AtmosphericLaw(
        key="cape_buoyancy_integral",
        name="Énergie Potentielle de Convection Disponible (CAPE)",
        domain="Thermodynamique",
        equation="CAPE = integral( g * (Tv_parcel - Tv_env) / Tv_env, dz )  [positively buoyant layers]",
        variables={
            "g": "Accélération de la pesanteur (9.80665 m/s²)",
            "Tv_parcel": "Température virtuelle de la parcelle",
            "Tv_env": "Température virtuelle de l'environnement",
            "z": "Altitude géométrique",
        },
        units={"CAPE": "J/kg", "Tv_parcel, Tv_env": "K", "z": "m"},
        description=(
            "Énergie disponible pour l'ascension convective d'une parcelle, intégrée par la méthode "
            "des trapèzes sur les couches à flottabilité positive. Utilise la température virtuelle "
            "si l'humidité est fournie."
        ),
        references=["Doswell & Rasmussen (1994), Wea. Forecasting 9(4), 625-629"],
        limitations=[
            "Théorie de la parcelle non entraînée (pas d'entraînement/détraînement).",
            "Intégration discrète par trapèzes : précision limitée par la résolution verticale du profil.",
        ],
        compute_func=lambda parcel_temperature, environment_temperature, height, **kw: CAPE.calculate(
            parcel_temperature, environment_temperature, height, **kw
        ),
    ),
    AtmosphericLaw(
        key="cin_buoyancy_integral",
        name="Inhibition Convective (CIN)",
        domain="Thermodynamique",
        equation="CIN = integral( g * (Tv_env - Tv_parcel) / Tv_env, dz )  [negatively buoyant layers]",
        variables={
            "g": "Accélération de la pesanteur (9.80665 m/s²)",
            "Tv_parcel": "Température virtuelle de la parcelle",
            "Tv_env": "Température virtuelle de l'environnement",
            "z": "Altitude géométrique",
        },
        units={"CIN": "J/kg (magnitude positive)", "Tv_parcel, Tv_env": "K", "z": "m"},
        description="Énergie à fournir pour surmonter la flottabilité négative sous le niveau de convection libre.",
        references=["Doswell & Rasmussen (1994), Wea. Forecasting 9(4), 625-629"],
        limitations=["Retourne une magnitude positive ; le signe conventionnel négatif est à appliquer par l'appelant."],
        compute_func=lambda parcel_temperature, environment_temperature, height, **kw: CIN.calculate(
            parcel_temperature, environment_temperature, height, **kw
        ),
    ),
    AtmosphericLaw(
        key="equivalent_potential_temperature_bolton_1980",
        name="Température Potentielle Équivalente (Bolton 1980, canonique ACF)",
        domain="Thermodynamique",
        equation=(
            "T_L = 56 + 1/(1/(Td-56) + ln(T/Td)/800); "
            "theta_L = T*(1000/(p-e))^kappa*(T/T_L)^(0.28r); "
            "theta_E = theta_L * exp(r*(1+0.448r)*(3036/T_L - 1.78))"
        ),
        variables={
            "T": "Température de l'air",
            "Td": "Température du point de rosée",
            "p": "Pression atmosphérique",
            "e": "Pression de vapeur réelle (= es(Td))",
            "r": "Rapport de mélange (kg/kg)",
            "kappa": "Rd/Cp",
        },
        units={"T, Td, T_L": "K", "p": "hPa", "r": "kg/kg", "theta_E": "K"},
        description=(
            "Formule empirique de référence pour theta_e, précise à ~0.3K. Implémentation ACF "
            "canonique (formulaire opérationnel repris de MetPy/SHARPpy)."
        ),
        references=["Bolton, D. (1980). Mon. Wea. Rev., 108(7), 1046-1053."],
        limitations=["Suppose une ascension pseudo-adiabatique réversible."],
        compute_func=lambda temperature_k, dewpoint_k, pressure_hpa: (
            EquivalentPotentialTemperature.calculate_bolton_1980(temperature_k, dewpoint_k, pressure_hpa)
        ),
    ),
    AtmosphericLaw(
        key="lcl_height_bolton_1980",
        name="Niveau de Condensation par Ascension (LCL, canonique ACF)",
        domain="Thermodynamique",
        equation="z_LCL = Cp * (T - T_L) / g  ;  T_L = 56 + 1/(1/(Td-56) + ln(T/Td)/800)",
        variables={
            "T": "Température de surface",
            "Td": "Point de rosée de surface",
            "T_L": "Température au LCL (Bolton 1980)",
            "Cp": "Chaleur spécifique à pression constante",
            "g": "Accélération de la pesanteur",
        },
        units={"T, Td, T_L": "K", "z_LCL": "m"},
        description=(
            "Hauteur du LCL dérivée de la conservation de l'énergie statique sèche entre la surface "
            "et le LCL, utilisant la température T_L de Bolton plutôt qu'un taux fixe empirique "
            "(règle d'Espy ~125 m/°C, conservée en parallèle pour compatibilité)."
        ),
        references=["Bolton, D. (1980). Mon. Wea. Rev., 108(7), 1046-1053.", "Holton & Hakim (2012)"],
        limitations=["Suppose une ascension purement adiabatique sèche jusqu'au LCL."],
        compute_func=lambda temperature_k, dewpoint_k: LCL.calculate_bolton(temperature_k, dewpoint_k),
    ),
]
