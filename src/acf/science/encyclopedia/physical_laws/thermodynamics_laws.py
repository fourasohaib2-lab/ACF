"""
Atmospheric Complexity Framework (ACF)

Fundamental Physical & Atmospheric Thermodynamics Laws Encyclopedia Module
"""

import math

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

# ---------------------------------------------------------------------------
# Computational Functions for Atmospheric Thermodynamics
# ---------------------------------------------------------------------------


def calculate_ideal_gas_pressure(rho: float, temp_k: float, r_d: float = 287.058) -> float:
    """Calcul de la pression d'un gaz parfait p = rho * Rd * T en Pa."""
    return rho * r_d * temp_k


def calculate_virtual_temperature(temp_k: float, q: float) -> float:
    """Calcul de la température virtuelle Tv = T * (1 + 0.608 * q) en K."""
    return temp_k * (1.0 + 0.608 * q)


def calculate_potential_temperature(temp_k: float, p_hpa: float, p0_hpa: float = 1000.0, kappa: float = 0.286) -> float:
    """Calcul de la température potentielle theta = T * (p0 / p)^0.286 en K."""
    if p_hpa <= 0.0:
        return temp_k
    return temp_k * ((p0_hpa / p_hpa) ** kappa)


def calculate_equivalent_potential_temperature(
    temp_k: float, p_hpa: float, q: float, lv: float = 2.5e6, cp: float = 1004.0
) -> float:
    """Calcul de la température potentielle équivalente theta_e = theta * exp(Lv * q / (cp * T)) en K."""
    theta = calculate_potential_temperature(temp_k, p_hpa)
    return theta * math.exp((lv * q) / (cp * temp_k))


def calculate_clausius_clapeyron_es(
    temp_k: float, es_0: float = 611.2, t0: float = 273.15, lv: float = 2.5e6, rv: float = 461.5
) -> float:
    """Pression de vapeur saturante es(T) via l'équation d'état de Clausius-Clapeyron en Pa."""
    return es_0 * math.exp((lv / rv) * (1.0 / t0 - 1.0 / temp_k))


def calculate_mixing_ratio(e_pa: float, p_pa: float, epsilon: float = 0.622) -> float:
    """Calcul du rapport de mélange w = epsilon * e / (p - e) en kg/kg."""
    denom = p_pa - e_pa
    if denom <= 0.0:
        return 0.0
    return (epsilon * e_pa) / denom


def calculate_specific_humidity(e_pa: float, p_pa: float, epsilon: float = 0.622) -> float:
    """Calcul de l'humidité spécifique q = epsilon * e / (p - (1 - epsilon)*e) en kg/kg."""
    denom = p_pa - (1.0 - epsilon) * e_pa
    if denom <= 0.0:
        return 0.0
    return (epsilon * e_pa) / denom


def calculate_relative_humidity(e_pa: float, es_pa: float) -> float:
    """Calcul de l'humidité relative RH = (e / es) * 100 en %."""
    if es_pa <= 0.0:
        return 0.0
    return min(max((e_pa / es_pa) * 100.0, 0.0), 100.0)


# ---------------------------------------------------------------------------
# Encyclopedia Entries
# ---------------------------------------------------------------------------

LAWS: list[EncyclopediaEntry] = [
    EncyclopediaEntry(
        # NOTE (correction - registry key collision): this used to be
        # registered as "ideal_gas_law", the SAME key as
        # encyclopedia/atmosphere.py's own "ideal_gas_law" entry (and the
        # foundational science/laws/atmospheric.py's ScientificRegistry
        # entry of the same name) - EncyclopediaRegistry.register() does
        # a silent `cls._entries[entry.key] = entry` with no collision
        # detection, so whichever of the two encyclopedia modules
        # happened to import last (a side effect of unrelated test
        # collection order, not a deliberate contract) silently won,
        # while the other became completely inaccessible. This was not
        # theoretical: pytest tests/test_scientific_encyclopedia.py and
        # tests/test_scientific_knowledge_engine.py (both hard-code
        # atmosphere.py's density/temperature-param signature) FAILED
        # when run in isolation or with `-k ideal_gas`, while a full
        # unfiltered `pytest tests/` run happened to pass by accidental
        # import ordering - exactly the "correct only by luck" pattern
        # this session's audit exists to catch. Renamed to a distinct
        # key so both formulations are independently accessible and
        # deterministic regardless of import order. See
        # EncyclopediaRegistry.register()'s new collision guard, added
        # in the same fix, which now makes any future accidental key
        # collision fail loudly at import time instead of silently.
        key="ideal_gas_law_thermodynamics",
        name="Loi des Gaz Parfaits Atmosphériques",
        domain="Thermodynamique Atmosphérique",
        subdomain="Équation d'état",
        equation="p = rho * Rd * T",
        latex_equation=r"p = \rho R_d T",
        variables={
            "p": "Pression atmosphérique (Pa)",
            "rho": "Masse volumique de l'air sec (kg/m³)",
            "Rd": "Constante de l'air sec (287.058 J/(kg·K))",
            "T": "Température absolue (K)",
        },
        units={"p": "Pa", "rho": "kg/m³", "T": "K"},
        description="Loi d'état fondamentale reliant la pression, la masse volumique et la température de l'air sec dans l'atmosphère terrestre.",
        application_conditions=["Troposphère et stratosphère sous conditions de pression standard"],
        limitations=["Nécessite la température virtuelle Tv pour l'air humide"],
        references=["WMO-No. 8", "AMS Glossary of Meteorology", "Bohren & Albrecht (1998)"],
        compute_func=calculate_ideal_gas_pressure,
    ),
    EncyclopediaEntry(
        key="van_der_waals_real_gas",
        name="Loi des Gaz Réels de Van der Waals",
        domain="Thermodynamique Atmosphérique",
        subdomain="Équation d'état",
        equation="(p + a/V^2) * (V - b) = R * T",
        latex_equation=r"\left(p + \frac{a}{V^2}\right)(V - b) = RT",
        variables={
            "p": "Pression (Pa)",
            "V": "Volume molaire (m³/mol)",
            "a": "Constante d'attraction intermoléculaire",
            "b": "Covolume des molécules",
        },
        units={"p": "Pa", "V": "m³/mol"},
        description="Extension de la loi des gaz parfaits prenant en compte le volume propre des molécules et les forces d'attraction intermoléculaires.",
        application_conditions=["Hautes pressions et basses températures"],
        limitations=["Déviations légères pour les fluides supercritiques"],
        references=["Van der Waals (1873)", "Bohren & Albrecht (1998)"],
    ),
    EncyclopediaEntry(
        key="virtual_temperature_law",
        name="Température Virtuelle (Tv)",
        domain="Thermodynamique Atmosphérique",
        subdomain="Variables d'état",
        equation="Tv = T * (1 + 0.608 * q)",
        latex_equation=r"T_v = T (1 + 0.608 q)",
        variables={"T": "Température absolue (K)", "q": "Humidité spécifique (kg/kg)"},
        units={"Tv": "K"},
        description="Température qu'aurait de l'air sec s'il possédait la même pression et la même masse volumique que l'air humide considéré.",
        application_conditions=["Calcul de flottabilité et équation hypsométrique"],
        limitations=["Approximation du premier ordre pour l'air humide non condensé"],
        references=["WMO Atmospheric Physics", "Emanuel (1994)"],
        compute_func=calculate_virtual_temperature,
    ),
    EncyclopediaEntry(
        key="potential_temperature_law",
        name="Température Potentielle (Theta)",
        domain="Thermodynamique Atmosphérique",
        subdomain="Variables conservées",
        equation="theta = T * (p0 / p)^0.286",
        latex_equation=r"\theta = T \left(\frac{p_0}{p}\right)^{\frac{R_d}{c_p}}",
        variables={
            "T": "Température (K)",
            "p": "Pression (hPa)",
            "p0": "Pression de référence (1000 hPa)",
            "Rd/cp": "0.286",
        },
        units={"theta": "K"},
        description="Température qu'aurait une parcelle d'air si elle était amenée de manière adiabatique sèche à la pression de référence p0 = 1000 hPa. Conservée lors des mouvements adiabatiques secs.",
        application_conditions=["Analyse de stabilité atmosphérique et dynamique dry-isentropique"],
        limitations=["Non conservée lors des changements de phase de l'eau (condensation/évaporation)"],
        references=["Poisson (1823)", "Holton & Hakim (2012)"],
        compute_func=calculate_potential_temperature,
    ),
    EncyclopediaEntry(
        key="equivalent_potential_temperature_law",
        name="Température Potentielle Équivalente (Theta_e)",
        domain="Thermodynamique Atmosphérique",
        subdomain="Variables conservées",
        equation="theta_e = theta * exp(Lv * q / (cp * T))",
        latex_equation=r"\theta_e \approx \theta \exp\left(\frac{L_v q}{c_p T}\right)",
        variables={
            "theta": "Température potentielle (K)",
            "Lv": "Chaleur latente de vaporisation (J/kg)",
            "q": "Humidité spécifique (kg/kg)",
            "cp": "Chaleur spécifique (1004 J/(kg·K))",
        },
        units={"theta_e": "K"},
        description="Température potentielle atteinte par une parcelle d'air après condensation complète de toute sa vapeur d'eau et libération de la chaleur latente associée. Conservée lors des mouvements pseudo-adiabatiques humides.",
        application_conditions=["Analyse des masses d'air convectives et fronts"],
        limitations=["Sensible aux formulations d'intégration de Bolton (1980)"],
        references=["Bolton (1980) Mon. Wea. Rev.", "Emanuel (1994)"],
        compute_func=calculate_equivalent_potential_temperature,
    ),
    EncyclopediaEntry(
        key="pseudo_equivalent_potential_temperature",
        name="Température Pseudo-Potentielle Équivalente (Theta_ep)",
        domain="Thermodynamique Atmosphérique",
        subdomain="Variables conservées",
        equation="theta_ep = theta * exp(Lv * w_sat / (cp * T_lcl))",
        latex_equation=r"\theta_{ep} = T \left(\frac{p_0}{p - e}\right)^{\frac{R_d}{c_p}} \exp\left(\frac{L_v w}{c_p T_{\text{LCL}}}\right)",
        variables={"T_LCL": "Température au niveau LCL (K)", "w": "Rapport de mélange"},
        units={"theta_ep": "K"},
        description="Variante de la température potentielle équivalente prenant en compte l'élimination instantanée de la précipitation formée (processus pseudo-adiabatique).",
        application_conditions=["Sondages aérologiques et convection profonde"],
        limitations=["Précipitations supposées quitter immédiatement la parcelle d'air"],
        references=["Bolton (1980)", "AMS Glossary"],
    ),
    EncyclopediaEntry(
        key="first_law_thermodynamics_atmos",
        name="Premier Principe de la Thermodynamique Atmosphérique",
        domain="Thermodynamique Atmosphérique",
        subdomain="Principes fondamentaux",
        equation="dq = du + dw = cp * dT - v * dp",
        latex_equation=r"dq = c_v dT + p dv = c_p dT - \alpha dp",
        variables={
            "dq": "Chaleur apportée (J/kg)",
            "cv": "718 J/(kg·K)",
            "cp": "1004 J/(kg·K)",
            "alpha": "Volume massique (m³/kg)",
        },
        units={"dq": "J/kg"},
        description="Bilan énergétique stipulant la conservation de l'énergie thermique, interne et du travail de pression au sein d'une parcelle d'air.",
        application_conditions=["Systèmes thermodynamiques atmosphériques fermés ou ouverts"],
        limitations=["Nécessite le suivi des termes de chauffage diabatique (rayonnement, chaleur latente)"],
        references=["WMO Physics", "Bohren & Albrecht (1998)"],
    ),
    EncyclopediaEntry(
        key="second_law_thermodynamics_atmos",
        name="Deuxième Principe de la Thermodynamique Atmosphérique",
        domain="Thermodynamique Atmosphérique",
        subdomain="Principes fondamentaux",
        equation="ds >= dq / T",
        latex_equation=r"ds \ge \frac{dq}{T}",
        variables={"ds": "Variation d'entropie spécifique (J/(kg·K))", "dq": "Chaleur échangée"},
        units={"ds": "J/(kg·K)"},
        description="Principe d'irréversibilité régissant le sens spontané des transferts thermiques et la production d'entropie lors du mélange turbulent et des précipitations.",
        application_conditions=["Processus réels irréversibles (mélange, diffusion, précipitation)"],
        limitations=["Égalité valide uniquement pour les processus réversibles idélisés"],
        references=["Bohren & Albrecht (1998)"],
    ),
    EncyclopediaEntry(
        key="atmospheric_entropy_law",
        name="Entropie Atmosphérique",
        domain="Thermodynamique Atmosphérique",
        subdomain="Variables d'état",
        equation="s = cp * ln(theta) + C",
        latex_equation=r"s = c_p \ln \theta + s_0",
        variables={"theta": "Température potentielle (K)", "cp": "1004 J/(kg·K)"},
        units={"s": "J/(kg·K)"},
        description="Mesure du désordre thermodynamique de l'air. L'entropie spécifique de l'air sec est directement proportionnelle au logarithme de la température potentielle.",
        application_conditions=["Écoulements isentropiques"],
        limitations=["Définition modifiée pour l'air humide condensé"],
        references=["Emanuel (1994)", "AMS Glossary"],
    ),
    EncyclopediaEntry(
        key="enthalpy_atmospheric_law",
        name="Enthalpie Atmosphérique (h)",
        domain="Thermodynamique Atmosphérique",
        subdomain="Fonctions d'état",
        equation="h = u + p * v = cp * T",
        latex_equation=r"h = u + p \alpha = c_p T",
        variables={"u": "Énergie interne", "alpha": "Volume specifique", "cp": "1004 J/(kg·K)"},
        units={"h": "J/kg"},
        description="Fonction d'état mesurant le contenu thermique total d'un fluide sous pression constante.",
        application_conditions=["Flux de chaleur de surface et bilans d'énergie"],
        limitations=["Sensible aux termes de chaleur latente lors des transitions de phase"],
        references=["Bohren & Albrecht (1998)"],
    ),
    EncyclopediaEntry(
        key="internal_energy_atmospheric",
        name="Énergie Interne Atmosphérique (u)",
        domain="Thermodynamique Atmosphérique",
        subdomain="Fonctions d'état",
        equation="u = cv * T",
        latex_equation=r"u = c_v T",
        variables={"cv": "Chaleur spécifique à volume constant (718 J/(kg·K))"},
        units={"u": "J/kg"},
        description="Somme de l'énergie cinétique et potentielle microscopique des molécules d'air.",
        application_conditions=["Bilans thermiques à volume constant"],
        limitations=["Néglige les modes de vibration aux températures très basses"],
        references=["Bohren & Albrecht (1998)"],
    ),
    EncyclopediaEntry(
        key="dry_adiabatic_process_law",
        name="Transformation Adiabatique Sèche",
        domain="Thermodynamique Atmosphérique",
        subdomain="Processus thermodynamiques",
        equation="dT/dz = - g / cp = - 9.8 deg C/km (Lapse rate sec)",
        latex_equation=r"\Gamma_d = -\frac{dT}{dz} = \frac{g}{c_p} \approx 9.8 \text{ K/km}",
        variables={"Gamma_d": "Gradient adiabatique sec (9.8 K/km)", "g": "9.81 m/s²", "cp": "1004 J/(kg·K)"},
        units={"Gamma_d": "K/m"},
        description="Refroidissement d'une parcelle d'air non condensée en ascendance sans échange de chaleur avec son environnement (dT/dz = -9.8 °C/km).",
        application_conditions=["Ascendance sous le LCL"],
        limitations=["Invalide dès qu'il y a condensation d'eau"],
        references=["WMO-No. 8", "Holton & Hakim (2012)"],
    ),
    EncyclopediaEntry(
        key="moist_pseudo_adiabatic_process",
        name="Transformation Pseudo-Adiabatique Humide",
        domain="Thermodynamique Atmosphérique",
        subdomain="Processus thermodynamiques",
        equation="dT/dz = - (g/cp) * (1 + Lv*q_sat / (Rd*T)) / (1 + Lv^2*q_sat / (cp*Rv*T^2))",
        latex_equation=r"\Gamma_m = -\frac{dT}{dz} = \frac{g}{c_p} \frac{1 + \frac{L_v q_{\text{sat}}}{R_d T}}{1 + \frac{L_v^2 q_{\text{sat}}}{c_p R_v T^2}}",
        variables={"Gamma_m": "Gradient pseudo-adiabatique humide (~ 5 à 6.5 K/km)"},
        units={"Gamma_m": "K/m"},
        description="Refroidissement d'une parcelle d'air saturée en ascendance, atténué par la libération continue de la chaleur latente de condensation.",
        application_conditions=["Ascendance nuageuse au-dessus du LCL"],
        limitations=[
            "Dépendance à la température (varie de 4 K/km dans les tropiques chauds à 9 K/km à très basse température)"
        ],
        references=["Bolton (1980)", "Emanuel (1994)"],
    ),
    EncyclopediaEntry(
        key="clausius_clapeyron_equation",
        name="Équation de Clausius-Clapeyron",
        domain="Thermodynamique Atmosphérique",
        subdomain="Changement de phase de l'eau",
        equation=(
            "Loi différentielle : des/dT = (L_v * es) / (R_v * T^2). calculate_clausius_clapeyron_es() "
            "retourne sa solution analytique intégrée (Lv, Rv constants) : "
            "es(T) = es0 * exp[(Lv/Rv)*(1/T0 - 1/T)]"
        ),
        latex_equation=r"\frac{de_s}{dT} = \frac{L_v e_s}{R_v T^2}",
        variables={
            "es": "Pression de vapeur saturante (Pa) - ce que calculate_clausius_clapeyron_es() retourne",
            "Lv": "Chaleur latente de vaporisation (2.5e6 J/kg)",
            "Rv": "Constante vapeur d'eau (461.5 J/(kg·K))",
        },
        units={"es": "Pa", "T": "K"},
        description="Relation différentielle fondamentale décrivant l'augmentation exponentielle de la capacité de retention d'eau de l'air avec la température (~7% par K).",
        application_conditions=["Équilibre liquide-vapeur ou glace-vapeur"],
        limitations=[
            "Lv varie légèrement avec la température",
            # NOTE (correction): "equation" previously stated only the
            # differential des/dT=... while calculate_clausius_clapeyron_es()
            # (its own docstring: "es(T) via l'equation d'etat de
            # Clausius-Clapeyron") actually returns es(T) itself (Pa), a
            # different quantity/unit than des/dT (Pa/K) - now both forms
            # are stated. This is the analytically-integrated, constant-Lv
            # solution - different from science/laws/thermodynamics.py's
            # 'clausius_clapeyron' entry, which uses the empirical
            # Bolton/Tetens fit instead; the two are NOT numerically
            # identical (they agree at T0=273.15K by construction, then
            # diverge with warming - ~0.9% apart at 290K). Cross-referenced
            # rather than silently duplicated per ACF's single-source-of-
            # truth convention.
        ],
        references=["Clausius (1850)", "Clapeyron (1834)", "WMO Technical Note"],
        compute_func=calculate_clausius_clapeyron_es,
    ),
    EncyclopediaEntry(
        key="dewpoint_temperature_law",
        name="Point de Rosée (Td)",
        domain="Thermodynamique Atmosphérique",
        subdomain="Variables d'humidité",
        equation="Td = (243.5 * ln(e/611.2)) / (17.67 - ln(e/611.2))",
        latex_equation=r"T_d = \frac{243.5 \ln(e/611.2)}{17.67 - \ln(e/611.2)}",
        variables={"e": "Pression de vapeur d'eau (Pa)"},
        units={"Td": "°C"},
        description="Température à laquelle il faut refroidir de l'air à pression et humidité constantes pour qu'il devienne saturé (formation de rosée ou brouillard).",
        application_conditions=["Calcul de la base des nuages LCL et confort thermique"],
        limitations=["Formule d'approximation de Magnus-Tetens valide entre -45°C et +60°C"],
        references=["Magnus (1844)", "WMO Guide to Instruments"],
    ),
    EncyclopediaEntry(
        key="mixing_ratio_humidity",
        name="Rapport de Mélange d'Humidité (w)",
        domain="Thermodynamique Atmosphérique",
        subdomain="Variables d'humidité",
        equation="w = 0.622 * e / (p - e)",
        latex_equation=r"w = \epsilon \frac{e}{p - e}",
        variables={"e": "Pression de vapeur d'eau (Pa)", "p": "Pression totale (Pa)", "epsilon": "Rd / Rv = 0.622"},
        units={"w": "kg/kg (ou g/kg)"},
        description="Rapport entre la masse de vapeur d'eau et la masse d'air sec dans un volume donné. Variable conservée lors des variations de pression.",
        application_conditions=["Sondages thermodynamiques et schémas NWP"],
        limitations=["Différent de l'humidité spécifique q qui rapporte à la masse d'air humide totale"],
        references=["WMO-No. 8", "AMS Glossary"],
        compute_func=calculate_mixing_ratio,
    ),
    EncyclopediaEntry(
        key="specific_humidity_law",
        name="Humidité Spécifique (q)",
        domain="Thermodynamique Atmosphérique",
        subdomain="Variables d'humidité",
        equation="q = 0.622 * e / (p - 0.378 * e)",
        latex_equation=r"q = \frac{m_v}{m_v + m_d} = \epsilon \frac{e}{p - (1-\epsilon)e}",
        variables={"mv": "Masse de vapeur", "md": "Masse d'air sec"},
        units={"q": "kg/kg"},
        description="Rapport entre la masse de vapeur d'eau et la masse totale d'air humide. Variable pronostique privilégiée dans les modèles NWP.",
        application_conditions=["Modèles de prévision numérique et assimilation"],
        limitations=["Différence minime avec w en air sec mais mesurable en région tropicale humide"],
        references=["WMO-No. 8", "ECMWF Physics Documentation"],
        compute_func=calculate_specific_humidity,
    ),
    EncyclopediaEntry(
        key="relative_humidity_law",
        name="Humidité Relative (RH)",
        domain="Thermodynamique Atmosphérique",
        subdomain="Variables d'humidité",
        equation="RH = (e / es) * 100",
        latex_equation=r"\text{RH} = \frac{e}{e_s(T)} \times 100\% = \frac{w}{w_{\text{sat}}} \times 100\%",
        variables={"e": "Pression de vapeur actuelle", "es": "Pression de vapeur à saturation à T"},
        units={"RH": "%"},
        description="Pourcentage de saturation de l'air par rapport à sa capacité maximale de rétention d'eau à la température T.",
        application_conditions=["Diagnostic de formation de brouillard, nuages et confort humain"],
        limitations=[
            "Fortement dépendant de la température (RH diminue quand T augmente à humidité absolue constante)"
        ],
        references=["WMO Guide to Meteorological Instruments", "NOAA NWS"],
        compute_func=calculate_relative_humidity,
    ),
]

for entry in LAWS:
    EncyclopediaRegistry.register(entry)
