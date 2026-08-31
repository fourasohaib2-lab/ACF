"""
Atmospheric Complexity Framework (ACF)

Complete WMO Cloud Classification & Microphysical Processes Encyclopedia Module
"""

import math
from typing import Any

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

# ---------------------------------------------------------------------------
# 1. Classification OMM Complète (10 Genres)
# ---------------------------------------------------------------------------

WMO_GENRES: list[dict[str, Any]] = [
    {
        "key": "wmo_cirrus",
        "name": "Cirrus (Ci)",
        "altitude_range_m": (6000, 12000),
        "typical_temp_c": (-60, -35),
        "composition": "Glace pure (cristaux prismatiques)",
        "precipitation": "Aucune au sol (Virga glacée)",
        "aviation_hazard": "Turbulence légère à modérée, Cristaux de glace (génération d'erreurs Pitot)",
        "satellite_signature": "Forte transparence en canal visible, Froid en IR 10.8µm",
    },
    {
        "key": "wmo_cirrostratus",
        "name": "Cirrostratus (Cs)",
        "altitude_range_m": (6000, 12000),
        "typical_temp_c": (-50, -30),
        "composition": "Glace pure",
        "precipitation": "Aucune au sol (Halos solaires et lunaires à 22°)",
        "aviation_hazard": "Léger givrage en sommet de couche",
        "satellite_signature": "Voile fin homogène à haute altitude en IR",
    },
    {
        "key": "wmo_cirrocumulus",
        "name": "Cirrocumulus (Cc)",
        "altitude_range_m": (6000, 10000),
        "typical_temp_c": (-40, -25),
        "composition": "Glace et gouttelettes de surenfusion (eau surfondue)",
        "precipitation": "Aucune",
        "aviation_hazard": "Turbulence légère d'onde convective",
        "satellite_signature": "Texture finement ridée en haute troposphère",
    },
    {
        "key": "wmo_altostratus",
        "name": "Altostratus (As)",
        "altitude_range_m": (2000, 7000),
        "typical_temp_c": (-25, 0),
        "composition": "Mélange eau surfondue et cristaux de glace",
        "precipitation": "Pluie ou neige continue modérée",
        "aviation_hazard": "Givrage modéré à fort, visibilité réduite en vol aux instruments",
        "satellite_signature": "Nappe grise continue en VIS, température moyenne en IR",
    },
    {
        "key": "wmo_altocumulus",
        "name": "Altocumulus (Ac)",
        "altitude_range_m": (2000, 6000),
        "typical_temp_c": (-20, 5),
        "composition": "Eau surfondue prédominante",
        "precipitation": "Virga occasionnelle, légères averses",
        "aviation_hazard": "Givrage modéré (gouttelettes surfondues), turbulence d'onde",
        "satellite_signature": "Mosaïque d'éléments globuleux en canal visible",
    },
    {
        "key": "wmo_nimbostratus",
        "name": "Nimbostratus (Ns)",
        "altitude_range_m": (500, 5000),
        "typical_temp_c": (-15, 10),
        "composition": "Eau liquide, eau surfondue, neige et glace",
        "precipitation": "Pluie ou neige continue forte et durable",
        "aviation_hazard": "Givrage sévère, turbulence de couche, plafond bas (IFR bas)",
        "satellite_signature": "Nappe très dense et opaque à large échelle en VIS et IR",
    },
    {
        "key": "wmo_stratus",
        "name": "Stratus (St)",
        "altitude_range_m": (0, 2000),
        "typical_temp_c": (-5, 15),
        "composition": "Gouttelettes d'eau liquide",
        "precipitation": "Bruine, neige en grain, brouillard élevé",
        "aviation_hazard": "Plafond extrêmement bas (conditions CAT II/III), visibilité minime",
        "satellite_signature": "Très brillant en VIS, signature chaude en IR (proche de la surface)",
    },
    {
        "key": "wmo_stratocumulus",
        "name": "Stratocumulus (Sc)",
        "altitude_range_m": (500, 2500),
        "typical_temp_c": (-10, 15),
        "composition": "Eau liquide et gouttelettes surfondues",
        "precipitation": "Pluie faible, bruine intermittente ou neige légère",
        "aviation_hazard": "Givrage en basse couche, turbulence de couche limite",
        "satellite_signature": "Champs organisés en rouleaux ou galets sombres/clairs",
    },
    {
        "key": "wmo_cumulus",
        "name": "Cumulus (Cu)",
        "altitude_range_m": (600, 3000),
        "typical_temp_c": (0, 20),
        "composition": "Gouttelettes d'eau liquide",
        "precipitation": "Averses faibles sous Cumulus congestus",
        "aviation_hazard": "Turbulence convective thermique en basses couches",
        "satellite_signature": "Petits éléments cotonneux à fort albedo en VIS",
    },
    {
        "key": "wmo_cumulonimbus",
        "name": "Cumulonimbus (Cb)",
        "altitude_range_m": (500, 18000),
        "typical_temp_c": (-65, 25),
        "composition": "Eau liquide à la base, eau surfondue au cœur, glace et grêle au sommet",
        "precipitation": "Averses torrentielles, grêle, orages, rafales de vent",
        "aviation_hazard": "Givrage sévère, Cisaillement de vent (microburst), Foudre, CAT extrême, Grêle",
        "satellite_signature": "Sommet extrêmement froid (< -60°C en IR), Enclume massive et ombres portées en VIS",
    },
]

for g in WMO_GENRES:
    entry = EncyclopediaEntry(
        key=g["key"],
        name=f"Genre OMM: {g['name']}",
        domain="Nuages & Microphysique",
        subdomain="Classification WMO",
        equation=f"Altitude: {g['altitude_range_m'][0]}-{g['altitude_range_m'][1]} m",
        latex_equation=rf"\text{{{g['name']}}} \quad h \in [{g['altitude_range_m'][0]}, {g['altitude_range_m'][1]}] \text{{ m}}",
        variables={
            "Altitude": f"{g['altitude_range_m']} m",
            "Température": f"{g['typical_temp_c']} °C",
            "Composition": g["composition"],
        },
        units={"Altitude": "m", "Température": "°C"},
        description=f"Genre nuageux officiel WMO. Précipitation: {g['precipitation']}. Danger aéronautique: {g['aviation_hazard']}.",
        application_conditions=[
            "Atlas International des Nuages OMM (WMO-No. 407)",
            "Observations météo aviation (ICAO Annex 3)",
        ],
        limitations=["Variabilité régionale selon la latitude et la saison"],
        references=[
            "WMO International Cloud Atlas (2017)",
            "ICAO Annex 3 Manual",
            "Météo-France Guide du Météorologiste",
        ],
    )
    EncyclopediaRegistry.register(entry)


# ---------------------------------------------------------------------------
# 2. Formation & Thermodynamic Niveaux Convectifs
# ---------------------------------------------------------------------------


def calculate_lcl_height(temp_c: float, dewpoint_c: float) -> float:
    """Calcul approché de l'altitude du LCL (Niveau de Condensation par Ascendance): z_LCL = 125 * (T - Td)."""
    return 125.0 * max(temp_c - dewpoint_c, 0.0)


def calculate_lfc_height(z_lcl: float, cape: float) -> float:
    """Calcul estimé du Niveau de Convection Libre (LFC)."""
    if cape <= 0.0:
        return z_lcl + 1500.0
    return max(z_lcl, z_lcl + 500.0 - (cape / 10.0))


def calculate_el_height(z_lfc: float, cape: float) -> float:
    """Calcul estimé du Niveau d'Équilibre Convectif (EL / Equilibrium Level)."""
    if cape <= 0.0:
        return z_lfc
    return z_lfc + 1000.0 + (cape * 3.5)


EncyclopediaRegistry.register(
    EncyclopediaEntry(
        key="lcl_height_equation",
        name="Niveau de Condensation par Ascendance (LCL)",
        domain="Nuages & Microphysique",
        subdomain="Thermodynamique des nuages",
        equation="z_LCL = 125 * (T - Td)",
        latex_equation=r"z_{\text{LCL}} = 125 \cdot (T - T_d)",
        variables={"T": "Température (°C)", "Td": "Point de rosée (°C)"},
        units={"z_LCL": "m"},
        description="Altitude estimée de la base des nuages convectifs générés par ascendance thermique.",
        application_conditions=["Atmosphère sous-nuageuse bien mélangée (couche limite convective)"],
        limitations=["Estimation empirique valide en basses couches"],
        references=["WMO Atmospheric Physics Manual", "Espy (1841) / Bolton (1980) Mon. Wea. Rev."],
        compute_func=calculate_lcl_height,
    )
)

EncyclopediaRegistry.register(
    EncyclopediaEntry(
        key="lfc_height_equation",
        name="Niveau de Convection Libre (LFC)",
        domain="Nuages & Microphysique",
        subdomain="Thermodynamique des nuages",
        equation="z_LFC = Level where parcel Tv becomes warmer than environmental Tv",
        latex_equation=r"z_{\text{LFC}}: T_{v,\text{parcel}}(z) = T_{v,\text{env}}(z) \quad (\text{avec } \frac{dT_v}{dz} > 0)",
        variables={
            "Tv_parcel": "Température virtuelle de la parcelle",
            "Tv_env": "Température virtuelle de l'environnement",
        },
        units={"z_LFC": "m"},
        description="Altitude à partir de laquelle une parcelle d'air ascendante devient plus chaude que son environnement et s'élève spontanément par flottabilité.",
        application_conditions=["Sondage thermodynamique (SKEW-T / Emagramme)"],
        limitations=["Dépend de l'entraînement d'air sec (entrainment)"],
        references=["WMO-No. 8", "NOAA SPC Stability Parameters"],
        compute_func=calculate_lfc_height,
    )
)

EncyclopediaRegistry.register(
    EncyclopediaEntry(
        key="el_height_equation",
        name="Niveau d'Équilibre Convectif (EL)",
        domain="Nuages & Microphysique",
        subdomain="Thermodynamique des nuages",
        equation="z_EL = Altitude au sommet du domaine d'instabilité (Tv_parcel = Tv_env)",
        latex_equation=r"z_{\text{EL}}: T_{v,\text{parcel}}(z) = T_{v,\text{env}}(z) \quad (\text{sommet du domaine CAPE})",
        variables={"Tv_parcel": "Température virtuelle parcelle", "Tv_env": "Température virtuelle environnement"},
        units={"z_EL": "m"},
        description="Altitude marquant le sommet du courant ascendant convectif (sommet de la tour convective ou base de l'enclume du Cumulonimbus).",
        application_conditions=["Convection libre"],
        limitations=["L'inertie convective peut entraîner un dépassement du sommet (overshooting top) au-dessus du EL"],
        references=["AMS Glossary of Meteorology", "ECMWF Convection Documentation"],
        compute_func=calculate_el_height,
    )
)


# ---------------------------------------------------------------------------
# 3. Processus Microphysiques Fondamentaux
# ---------------------------------------------------------------------------


def bergeron_findeisen_diff(temp_c: float) -> float:
    """Calcule la différence de pression de vapeur saturante (e_w - e_i) en Pa.

    NOTE (correction): e_i's coefficients used 22.58/273.16 - close to but not
    matching the standard Alduchov & Eskridge (1996) ice-formula fit
    (611.21, 22.587, 273.86; verified via WebSearch), and 273.16 (the triple
    point of water in Kelvin) is a suspicious value to see as a Magnus-form
    denominator offset rather than the fitted 273.86. Numerical impact was
    small (~1% in the typical subzero range) but corrected to the standard
    reference coefficients per the golden rule (most-cited source). e_w
    (Bolton 1980 / Magnus-Tetens: 611.2, 17.67, 243.5) was already exact.
    """
    e_w = 611.2 * math.exp((17.67 * temp_c) / (temp_c + 243.5))
    e_i = 611.21 * math.exp((22.587 * temp_c) / (temp_c + 273.86))
    return max(e_w - e_i, 0.0)


def collision_coalescence_rate(r1_m: float, r2_m: float, kernel_k: float = 1.0e8) -> float:
    """Vitesse d'accroissement du rayon de la goutte par collision-coalescence: dr/dt = K * (r1 + r2)^2."""
    return kernel_k * ((r1_m + r2_m) ** 2)


def kessler_autoconversion_rate(qc: float, qc0: float = 1.0e-3, k_conv: float = 1.0e-3) -> float:
    """Taux d'autoconversion de Kessler: dqr/dt = C * max(qc - qc0, 0)."""
    return k_conv * max(qc - qc0, 0.0)


MICROPHYSICAL_PROCESSES: list[dict[str, Any]] = [
    {
        "key": "bergeron_findeisen_process",
        "name": "Effet Bergeron-Findeisen-Wegener",
        "subdomain": "Microphysique mixte",
        "equation": "e_i(T) < e_w(T)",
        "latex_equation": r"e_i(T) < e_w(T) \implies \frac{dq_i}{dt} > 0, \quad \frac{dq_c}{dt} < 0",
        "variables": {"temp_c": "Température sous zéro (°C)", "delta_e": "Différence e_w - e_i (Pa)"},
        "units": {"delta_e": "Pa"},
        "description": "Croissance rapide des cristaux de glace aux dépens des gouttelettes d'eau surfrondue en raison du gradient de pression de vapeur saturante.",
        "references": [
            "Bergeron (1935)",
            "Findeisen (1938)",
            "WMO Microphysics Guide",
            "Alduchov & Eskridge (1996) J. Appl. Meteor. (ice saturation vapor pressure fit)",
        ],
        "compute_func": bergeron_findeisen_diff,
    },
    {
        "key": "collision_coalescence_process",
        "name": "Processus de Collision-Coalescence",
        "subdomain": "Microphysique chaude",
        "equation": "dr/dt = K * (r1 + r2)^2",
        "latex_equation": r"\frac{dr}{dt} = K (r_1 + r_2)^2 E(r_1, r_2)",
        "variables": {
            "r1": "Rayon goutte collectrice (m)",
            "r2": "Rayon goutte collectée (m)",
            "K": "Noyau de collection (m³/s)",
        },
        "units": {"dr_dt": "m/s"},
        "description": "Grossissement des gouttes de pluie par choc et fusion entre gouttes de vitesses terminales différentes dans les nuages chauds.",
        "references": ["Pruppacher & Klett (1997)", "AMS Cloud Physics"],
        "compute_func": collision_coalescence_rate,
    },
    {
        "key": "kessler_autoconversion_process",
        "name": "Autoconversion de Kessler",
        "subdomain": "Paramétrisation NWP",
        "equation": "dq_r/dt = C * max(q_c - q_c0, 0)",
        "latex_equation": r"\left(\frac{\partial q_r}{\partial t}\right)_{\text{auto}} = C_{\text{kess}} \max(q_c - q_{c0}, 0)",
        "variables": {"qc": "Rapport de mélange eau nuageuse (kg/kg)", "qc0": "Seuil d'autoconversion (kg/kg)"},
        "units": {"dq_r_dt": "kg/(kg·s)"},
        "description": "Paramétrisation classique de conversion de l'eau nuageuse fine en eau de pluie précipitante au-delà d'un seuil critique qc0.",
        "references": ["Kessler (1969) Meteor. Monogr.", "NOAA / WRF Microphysics Manual"],
        "compute_func": kessler_autoconversion_rate,
    },
    {
        "key": "condensation_process",
        "name": "Condensation de la Vapeur d'Eau",
        "subdomain": "Changements de phase",
        "equation": "dq_c/dt = (q_v - q_sat) / tau_cond",
        "latex_equation": r"\frac{\partial q_c}{\partial t} = \frac{q_v - q_{\text{sat}}(T)}{\tau_{\text{cond}}}",
        "variables": {"qv": "Vapeur d'eau", "qsat": "Vapeur à saturation"},
        "units": {"rate": "kg/(kg·s)"},
        "description": "Passage de la phase vapeur à la phase liquide lors du refroidissement ou de l'ascendance au-delà du LCL.",
        "references": ["Rogers & Yau (1989)", "Météo-France ICE3/ICE4 Manual"],
    },
    {
        "key": "evaporation_process",
        "name": "Évaporation des Gouttes et Gouttelettes",
        "subdomain": "Changements de phase",
        "equation": "dq_v/dt = - (q_sat - q_v) / tau_evap",
        "latex_equation": r"\frac{\partial q_v}{\partial t} = \frac{q_{\text{sat}}(T) - q_v}{\tau_{\text{evap}}}",
        "variables": {"qv": "Vapeur d'eau", "qsat": "Vapeur à saturation"},
        "units": {"rate": "kg/(kg·s)"},
        "description": "Passage de l'état liquide à l'état vapeur dans un environnement sous-saturé (refroidissement sous-nuageux par évaporation).",
        "references": ["Pruppacher & Klett (1997)", "ECMWF Physics Documentation"],
    },
    {
        "key": "sublimation_process",
        "name": "Sublimation de la Glace",
        "subdomain": "Changements de phase",
        "equation": "dq_v/dt = S_sub (glace -> vapeur)",
        "latex_equation": r"\left(\frac{\partial q_v}{\partial t}\right)_{\text{sub}} = f(q_i, S_i < 0)",
        "variables": {"qi": "Glace/neige/graupel", "Si": "Sous-saturation par rapport à la glace"},
        "units": {"rate": "kg/(kg·s)"},
        "description": "Passage direct des hydrométéores glacés de la phase solide à la phase vapeur dans l'air sec.",
        "references": ["Pruppacher & Klett (1997)"],
    },
    {
        "key": "deposition_process",
        "name": "Déposition (Nucléation/Croissance Glacée)",
        "subdomain": "Changements de phase",
        "equation": "dq_i/dt = S_dep (vapeur -> glace)",
        "latex_equation": r"\left(\frac{\partial q_i}{\partial t}\right)_{\text{dep}} = f(q_v - q_{s,i})",
        "variables": {"qv": "Vapeur d'eau", "qsi": "Saturation sur glace"},
        "units": {"rate": "kg/(kg·s)"},
        "description": "Passage direct de la vapeur d'eau à la phase solide sur des noyaux glaçogènes (IN).",
        "references": ["Seifert & Beheng (2006)"],
    },
    {
        "key": "freezing_process",
        "name": "Congélation (Freezing / Homogène & Hétérogène)",
        "subdomain": "Changements de phase",
        "equation": "T < 0°C (hétérogène) / T < -38°C (homogène)",
        "latex_equation": r"\left(\frac{\partial q_i}{\partial t}\right)_{\text{frz}} = J_{\text{hom}}(T) q_c + J_{\text{het}}(T, \text{IN}) q_c",
        "variables": {"T": "Température (°C)", "IN": "Noyaux glaçogènes"},
        "units": {"rate": "kg/(kg·s)"},
        "description": "Congélation des gouttes surfondues. Homogène en dessous de -38°C et hétérogène en présence de noyaux glaçogènes.",
        "references": ["Pruppacher & Klett (1997)", "AROME ICE3 Manual"],
    },
    {
        "key": "melting_process",
        "name": "Fusion des Hydrométéores Glacés",
        "subdomain": "Changements de phase",
        "equation": "T > 0°C (glace/neige/graupel -> eau de pluie)",
        "latex_equation": r"\left(\frac{\partial q_r}{\partial t}\right)_{\text{mlt}} = -\frac{2\pi k_a}{L_f} (T - T_0) f(\text{Vent})",
        "variables": {"T": "Température (°C)", "Lf": "Chaleur latente de fusion (3.34e5 J/kg)"},
        "units": {"rate": "kg/(kg·s)"},
        "description": "Fusion des éléments glacés en franchissant l'isotherme 0°C (création de la couche brillante ou bright band sur les radars).",
        "references": ["WMO Radar & Cloud Physics Manuals"],
    },
    {
        "key": "riming_process",
        "name": "Givrage / Captation (Riming)",
        "subdomain": "Microphysique mixte",
        "equation": "glace/neige + gouttelettes surfondues -> graupel",
        "latex_equation": r"\left(\frac{\partial q_g}{\partial t}\right)_{\text{rim}} = E_{\text{rim}} \pi R^2 |V_s - V_c| q_c",
        "variables": {"qc": "Eau surfondue", "Es": "Efficacité de collecte"},
        "units": {"rate": "kg/(kg·s)"},
        "description": "Collecte et congélation instantanée de gouttelettes de surenfusion par des cristaux de glace ou flocons de neige formant du graupel ou de la grêle.",
        "references": ["Pinty & Jabouille (1998)", "Meso-NH Scientific Documentation"],
    },
    {
        "key": "aggregation_process",
        "name": "Agrégation des Cristaux de Glace",
        "subdomain": "Microphysique froide",
        "equation": "cristaux de glace -> flocons de neige",
        "latex_equation": r"\left(\frac{\partial q_s}{\partial t}\right)_{\text{agg}} = K_{\text{agg}}(T) q_i^2",
        "variables": {"qi": "Concentration de glace", "Kagg": "Coefficient d'agrégation"},
        "units": {"rate": "kg/(kg·s)"},
        "description": "Accroissement des flocons de neige par collisions entre cristaux de glace individuels.",
        "references": ["Morrison et al. (2009)", "Thompson et al. (2008)"],
    },
    {
        "key": "accretion_process",
        "name": "Accrétion (Collecte Pluie-Gouttelettes)",
        "subdomain": "Microphysique chaude",
        "equation": "dq_r/dt = E_acc * q_r * q_c",
        "latex_equation": r"\left(\frac{\partial q_r}{\partial t}\right)_{\text{acc}} = E_{\text{acc}} \pi R_r^2 (V_r - V_c) q_c",
        "variables": {"qr": "Pluie", "qc": "Nuage", "Eacc": "Efficacité d'accrétion"},
        "units": {"rate": "kg/(kg·s)"},
        "description": "Captation d'eau nuageuse fine par des gouttes de pluie précipitantes en tombant.",
        "references": ["Kessler (1969)", "AROME / WRF Microphysics Manual"],
    },
]

for p in MICROPHYSICAL_PROCESSES:
    entry_kwargs = {
        "key": p["key"],
        "name": p["name"],
        "domain": "Nuages & Microphysique",
        "subdomain": p["subdomain"],
        "equation": p["equation"],
        "latex_equation": p["latex_equation"],
        "variables": p["variables"],
        "units": p["units"],
        "description": p["description"],
        "application_conditions": ["Modélisation microphysique des nuages", "Schémas NWP (AROME, WRF, ECMWF, ICON)"],
        "limitations": ["Incertitudes sur les efficacités de collecte et lois de distribution en taille"],
        "references": p["references"],
    }
    if "compute_func" in p:
        entry_kwargs["compute_func"] = p["compute_func"]

    EncyclopediaRegistry.register(EncyclopediaEntry(**entry_kwargs))


# ---------------------------------------------------------------------------
# 4. Classificateur WMO
# ---------------------------------------------------------------------------


class WMOCloudClassifier:
    """
    Classificateur scientifique d'espèces et genres nuageux OMM (WMO-No. 407).
    """

    def classify_genre(self, base_m: float, temp_c: float, vertical_extension_m: float) -> str:
        """
        Détermine le genre nuageux WMO probable en fonction de la base, de la température et du développement vertical.
        """
        if vertical_extension_m > 6000 and temp_c < 0:
            return "Cumulonimbus (Cb)"
        if vertical_extension_m > 3000 and base_m < 1500:
            return "Nimbostratus (Ns)"
        if base_m > 6000:
            if vertical_extension_m < 1000:
                return "Cirrus (Ci) / Cirrostratus (Cs)"
            return "Cirrocumulus (Cc)"
        if base_m > 2000:
            if vertical_extension_m > 2000:
                return "Altostratus (As)"
            return "Altocumulus (Ac)"
        if vertical_extension_m > 1500:
            return "Cumulus (Cu)"
        if base_m < 500:
            return "Stratus (St)"
        return "Stratocumulus (Sc)"
