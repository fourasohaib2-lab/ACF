"""
Atmospheric Complexity Framework (ACF)

Convection & Severe Convective Weather Encyclopedia Module (CAPE, CIN, Indices, Convective Dynamics)
"""

import math

from acf.science.cape import CAPE
from acf.science.cin import CIN
from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry
from acf.science.severe_weather import SevereWeather
from acf.science.sweat_index import SWEATIndex

# ---------------------------------------------------------------------------
# Computational Functions for Convective Parameters & Stability Indices
# ---------------------------------------------------------------------------
#
# NOTE (single-source-of-truth cleanup): compute_cape/compute_cin/
# compute_sweat_index/compute_scp_index/compute_stp_index below used to
# be independent reimplementations of formulas already verified and
# tested in science/cape.py, science/cin.py, science/sweat_index.py and
# science/severe_weather.py. compute_scp_index and compute_stp_index in
# particular were LESS accurate than the canonical versions (missing
# the shear-term capping and CIN term that science/severe_weather.py's
# implementations have, verified against the SPC's own published
# formula). All five now delegate to the canonical implementations
# instead of duplicating (possibly-diverging) logic, while keeping
# their historical parameter names for backward compatibility with
# tests/test_atmospheric_encyclopedia_expansion.py.


def compute_cape(tv_parcel: list[float], tv_env: list[float], dz: float = 100.0) -> float:
    """
    CAPE (J/kg) from virtual-temperature profiles on a uniform grid
    spacing dz. Delegates to the canonical CAPE.calculate() (trapezoidal
    integration) instead of a hand-rolled Riemann sum.
    """
    height = [i * dz for i in range(len(tv_parcel))]
    return CAPE.calculate(tv_parcel, tv_env, height, is_kelvin=True)


def compute_cin(tv_parcel: list[float], tv_env: list[float], dz: float = 100.0) -> float:
    """CIN (J/kg), mirror of compute_cape() above. Delegates to CIN.calculate()."""
    height = [i * dz for i in range(len(tv_parcel))]
    return CIN.calculate(tv_parcel, tv_env, height, is_kelvin=True)


def compute_lifted_index(t_env_500_c: float, t_parcel_500_c: float) -> float:
    """Lifted Index (LI): LI = T_env_500 - T_parcel_500."""
    return t_env_500_c - t_parcel_500_c


def compute_showalter_index(t_env_500_c: float, t_parcel_850_to_500_c: float) -> float:
    """Showalter Index (SI): SI = T_env_500 - T_parcel_850_to_500."""
    return t_env_500_c - t_parcel_850_to_500_c


def compute_k_index(t850_c: float, t500_c: float, td850_c: float, t700_c: float, td700_c: float) -> float:
    """K Index (KI): KI = (T850 - T500) + Td850 - (T700 - Td700)."""
    return (t850_c - t500_c) + td850_c - (t700_c - td700_c)


def compute_total_totals(t850_c: float, t500_c: float, td850_c: float) -> float:
    """Total Totals Index (TT): TT = Vertical Totals + Cross Totals = (T850 - T500) + (Td850 - T500)."""
    return (t850_c - t500_c) + (td850_c - t500_c)


def compute_sweat_index(
    td850_c: float, tt: float, f850_kt: float, f500_kt: float, wdir850_deg: float, wdir500_deg: float
) -> float:
    """SWEAT Index. Delegates to the canonical, verified SWEATIndex.calculate()."""
    return SWEATIndex.calculate(
        td850=td850_c, tt=tt, wind850=f850_kt, wind500=f500_kt, dir850=wdir850_deg, dir500=wdir500_deg
    )


def compute_scp_index(cape: float, srh3km: float, bwd6km: float, mucin: float = 0.0) -> float:
    """
    Supercell Composite Parameter (SCP). Delegates to
    SevereWeather.supercell_composite_parameter() (SPC-verified: shear
    term capped at [0,1], CIN term included). mucin defaults to 0.0
    (CIN term = 1.0, i.e. "no CIN penalty"), matching this function's
    historical 3-argument signature for callers that don't supply it.
    """
    return SevereWeather.supercell_composite_parameter(
        mucape=cape, effective_srh=srh3km, effective_bulk_shear=bwd6km, mucin=mucin
    )


def compute_stp_index(cape: float, srh1km: float, lcl_m: float, shear6km: float) -> float:
    """
    Significant Tornado Parameter (STP), fixed-layer variant. Delegates
    to SevereWeather.significant_tornado_parameter_fixed() (SPC-
    verified: LCL and shear terms capped, matching the primary source).
    """
    return SevereWeather.significant_tornado_parameter_fixed(
        sbcape=cape, sblcl_m=lcl_m, srh_1km=srh1km, shear_6km=shear6km
    )


def compute_downdraft_speed_and_gust_front(dcape: float, reduced_gravity: float, cold_pool_depth_m: float, gust_front_coefficient: float = 1.0) -> dict[str, float]:
    """
    w_down = -sqrt(2*DCAPE) (m/s, négatif = descendant),
    V_gust = C*sqrt(g_prime*h) (m/s, front de rafales).

    NOTE (correction): equation field is fully explicit but this entry
    had no compute_func. w_down is returned NEGATIVE (downward
    velocity), matching the entry's own latex_equation
    (w_down = -sqrt(2*DCAPE)) even though its plain-text "equation"
    field omits the minus sign - the physical quantity is a downdraft,
    which is downward by definition.

    Parameters
    ----------
    dcape : float
        Downdraft CAPE (J/kg), >= 0.
    reduced_gravity : float
        g' = g*(delta_theta/theta0) (m/s^2), > 0.
    cold_pool_depth_m : float
        Épaisseur h du bassin d'air froid (m), >= 0.
    gust_front_coefficient : float
        Constante empirique C (dimensionless), défaut 1.0 (pas une
        valeur citée universellement - l'appelant doit fournir la
        valeur vérifiée pour son cas d'usage si différente).
    """
    if dcape < 0.0:
        raise ValueError("dcape must be non-negative.")
    if reduced_gravity < 0.0 or cold_pool_depth_m < 0.0:
        raise ValueError("reduced_gravity and cold_pool_depth_m must be non-negative.")
    w_down = -math.sqrt(2.0 * dcape)
    v_gust = gust_front_coefficient * math.sqrt(reduced_gravity * cold_pool_depth_m)
    return {"w_down_m_s": w_down, "v_gust_m_s": v_gust}


def compute_entrainment_detrainment_mass_flux_gradient(entrainment_rate: float, detrainment_rate: float, mass_flux: float) -> float:
    """
    dM/dz = (epsilon - delta) * M, en kg/(s*m).

    NOTE (correction): equation field is fully explicit but this entry
    had no compute_func.
    """
    return (entrainment_rate - detrainment_rate) * mass_flux


# ---------------------------------------------------------------------------
# Encyclopedia Entries
# ---------------------------------------------------------------------------

ENTRIES: list[EncyclopediaEntry] = [
    EncyclopediaEntry(
        key="cape_convective_energy",
        name="Énergie Potentielle Convective Disponible (CAPE)",
        domain="Convection & Orages",
        subdomain="Thermodynamique convective",
        equation="CAPE = int g * (Tv_parcel - Tv_env) / Tv_env dz",
        latex_equation=r"\text{CAPE} = \int_{z_{\text{LFC}}}^{z_{\text{EL}}} g \frac{T_{v,\text{parcel}} - T_{v,\text{env}}}{T_{v,\text{env}}} \, dz",
        variables={
            "Tv_parcel": "Température virtuelle parcelle (K)",
            "Tv_env": "Température virtuelle environnement (K)",
        },
        units={"CAPE": "J/kg"},
        description="Quantité maximale d'énergie d'accélération verticale disponible pour une parcelle d'air montant du LFC au niveau d'équilibre EL.",
        application_conditions=["Prévision d'instabilité atmosphérique, orages violents"],
        limitations=[
            "Sensible aux profils d'humidité en basse couche et au choix du type de parcelle (Surface, Mixed-Layer, Most-Unstable)"
        ],
        references=["Moncrieff & Miller (1976)", "NOAA SPC Severe Weather Parameters", "WMO-No. 8"],
        compute_func=compute_cape,
    ),
    EncyclopediaEntry(
        key="cin_convective_inhibition",
        name="Inhibition Convective (CIN)",
        domain="Convection & Orages",
        subdomain="Thermodynamique convective",
        equation="CIN = int g * (Tv_env - Tv_parcel) / Tv_env dz",
        latex_equation=r"\text{CIN} = \int_{z_{\text{surface}}}^{z_{\text{LFC}}} g \frac{T_{v,\text{env}} - T_{v,\text{parcel}}}{T_{v,\text{env}}} \, dz",
        variables={"Tv_parcel": "Température virtuelle parcelle", "Tv_env": "Température virtuelle environnement"},
        units={"CIN": "J/kg"},
        description="Quantité d'énergie négative (barrière thermique ou d'inversion) qu'une parcelle doit surmonter pour atteindre son niveau de convection libre LFC.",
        application_conditions=["Déclenchement des orages et estimation du blocage convectif"],
        limitations=["Une CIN trop forte (> 200 J/kg) empêche totalement le déclenchement des orages"],
        references=["Colby (1984) Mon. Wea. Rev.", "NOAA SPC Manual"],
        compute_func=compute_cin,
    ),
    EncyclopediaEntry(
        key="lifted_index_li",
        name="Lifted Index (LI)",
        domain="Convection & Orages",
        subdomain="Indices de stabilité",
        equation="LI = T_env(500hPa) - T_parcel(500hPa)",
        latex_equation=r"\text{LI} = T_{\text{env}, 500} - T_{\text{parcel}, 500}",
        variables={
            "T_env": "Température environnement à 500 hPa (°C)",
            "T_parcel": "Température parcelle soulevée à 500 hPa (°C)",
        },
        units={"LI": "°C"},
        description="Indice d'instabilité mesurant la différence de température à 500 hPa. LI < -6 °C indique une forte instabilité convective.",
        application_conditions=["Analyse de stabilité sous-synoptique"],
        limitations=["Évalué à un seul niveau de pression (500 hPa)"],
        references=["Galway (1956) Bull. Amer. Meteor. Soc.", "NOAA NWS Directives"],
        compute_func=compute_lifted_index,
    ),
    EncyclopediaEntry(
        key="showalter_index_si",
        name="Indice de Showalter (SI)",
        domain="Convection & Orages",
        subdomain="Indices de stabilité",
        equation="SI = T_env(500hPa) - T_parcel(850->500hPa)",
        latex_equation=r"\text{SI} = T_{\text{env}, 500} - T_{\text{parcel}, 850 \to 500}",
        variables={
            "T_env": "Température environnement à 500 hPa (°C)",
            "T_parcel": "Parcelle soulevée depuis 850 hPa à 500 hPa (°C)",
        },
        units={"SI": "°C"},
        description="Indice d'instabilité évitant l'influence des inversions nocturnes de surface en élevant la parcelle depuis 850 hPa.",
        application_conditions=["Prévision des orages nocturnes et convection élevée (elevated convection)"],
        limitations=["Moins sensible à l'humidité de la couche de surface"],
        references=["Showalter (1953) Bull. Amer. Meteor. Soc."],
        compute_func=compute_showalter_index,
    ),
    EncyclopediaEntry(
        key="k_index_ki",
        name="Indice K (K Index)",
        domain="Convection & Orages",
        subdomain="Indices de stabilité",
        equation="KI = (T850 - T500) + Td850 - (T700 - Td700)",
        latex_equation=r"\text{KI} = (T_{850} - T_{500}) + T_{d,850} - (T_{700} - T_{d,700})",
        variables={
            "T850, T500, T700": "Températures aux niveaux de pression (°C)",
            "Td850, Td700": "Points de rosée (°C)",
        },
        units={"KI": "°C"},
        description="Indice évaluant le potentiel d'averses et d'orages non sévéres en intégrant le gradient thermique vertical et l'humidité en moyenne/basse couche.",
        application_conditions=[
            "Prévision des averses de masse d'air et orages d'été (KI > 35 indique forte probabilité d'orages)"
        ],
        limitations=["Peu adapté aux orages supercellulaires et phénomènes violents"],
        references=["George (1960) Weather Forecasting for Aeronautics"],
        compute_func=compute_k_index,
    ),
    EncyclopediaEntry(
        key="total_totals_index",
        name="Indice Total Totals (TT)",
        domain="Convection & Orages",
        subdomain="Indices de stabilité",
        equation="TT = (T850 - T500) + (Td850 - T500)",
        latex_equation=r"\text{TT} = \text{VT} + \text{CT} = (T_{850} - T_{500}) + (T_{d,850} - T_{500})",
        variables={"VT": "Vertical Totals (T850 - T500)", "CT": "Cross Totals (Td850 - T500)"},
        units={"TT": "°C"},
        description="Indice combinant le lapse rate 850-500 hPa et l'humidité à 850 hPa. TT > 50 °C indique un risque d'orages forts à violents.",
        application_conditions=["Détection d'instabilité méso-échelle"],
        limitations=["Ne prend pas en compte le cisaillement du vent"],
        references=["Miller (1972) USAF Air Weather Service Tech Report"],
        compute_func=compute_total_totals,
    ),
    EncyclopediaEntry(
        key="sweat_index_severe",
        name="Indice SWEAT (Severe Weather Threat Index)",
        domain="Convection & Orages",
        subdomain="Indices de stabilité & cisaillement",
        equation="SWEAT = 12*Td850 + 20*(TT - 49) + 2*f850 + f500 + 125*(sin(wdir500-wdir850) + 0.2)",
        latex_equation=r"\text{SWEAT} = 12 T_{d,850} + 20(\text{TT}-49) + 2 f_{850} + f_{500} + 125[\sin(\theta_{500}-\theta_{850})+0.2]",
        variables={
            "Td850": "Point de rosée à 850 hPa",
            "TT": "Total Totals",
            "f850, f500": "Vitesse du vent (kt)",
            "theta": "Direction du vent",
        },
        units={"SWEAT": "dimensionless"},
        description="Indice composite intégrant thermodynamique et cinématique (cisaillement et advection de vorticité) pour évaluer la sévérité des orages (SWEAT > 300 = orages violents, > 400 = tornades).",
        application_conditions=["Prévision d'orages violents et tornades"],
        limitations=["Formulation complexe dépendante des seuils de vent"],
        references=["Miller (1972)", "NOAA Air Weather Service Manual"],
        compute_func=compute_sweat_index,
    ),
    EncyclopediaEntry(
        key="scp_supercell_composite",
        name="Supercell Composite Parameter (SCP)",
        domain="Convection & Orages",
        subdomain="Paramètres orageux violents",
        equation="SCP = (CAPE / 1000) * (SRH3km / 50) * (BWD6km / 20)",
        latex_equation=r"\text{SCP} = \left(\frac{\text{CAPE}}{1000}\right) \left(\frac{\text{SRH}_{0-3}}{50}\right) \left(\frac{\Delta V_{0-6}}{20}\right)",
        variables={"CAPE": "J/kg", "SRH3km": "Hélicité 0-3km (m²/s²)", "BWD6km": "Cisaillement 0-6km (m/s)"},
        units={"SCP": "dimensionless"},
        description="Indice composite de la NOAA SPC identifiant les environnements propices au développement de supercellules (SCP > 1.0).",
        application_conditions=["Analyse des environnements supercellulaires"],
        limitations=["Non spécifique au risque tornadique (couvert par le STP)"],
        references=["Thompson et al. (2003) Wea. Forecasting", "NOAA SPC Guide"],
        compute_func=compute_scp_index,
    ),
    EncyclopediaEntry(
        key="stp_index_tornado",
        name="Significant Tornado Parameter (STP)",
        domain="Convection & Orages",
        subdomain="Paramètres orageux violents",
        equation="STP = (CAPE/1500)*(SRH1km/150)*((2000-LCL)/1000)*(Shear6km/20)",
        latex_equation=r"\text{STP} = \left(\frac{\text{CAPE}}{1500}\right) \left(\frac{\text{SRH}_{0-1}}{150}\right) \left(\frac{2000 - z_{\text{LCL}}}{1000}\right) \left(\frac{\Delta V_{0-6}}{20}\right)",
        variables={"CAPE": "J/kg", "SRH1km": "m²/s²", "zLCL": "m", "Shear6km": "m/s"},
        units={"STP": "dimensionless"},
        description="Indice composite NOAA SPC prédisant la probabilité de tornades d'intensité EF2 ou plus sous des supercellules (STP > 1.0).",
        application_conditions=["Environnements orageux à fort cisaillement et basse base des nuages"],
        limitations=["Valeurs dépendantes de la précision du profil de vent en très basse couche"],
        references=["Thompson et al. (2003) Wea. Forecasting", "NOAA SPC Severe Weather Manual"],
        compute_func=compute_stp_index,
    ),
    # ---------------------------------------------------------------------------
    # Convective Dynamics & Processus
    # ---------------------------------------------------------------------------
    EncyclopediaEntry(
        key="deep_convection_process",
        name="Convection Profonde Troposphérique",
        domain="Convection & Orages",
        subdomain="Dynamique convective",
        equation="dw/dt = g * (Tv_parcel - Tv_env) / Tv_env - g * q_liquid + Drag",
        latex_equation=r"\frac{dw}{dt} = g \left(\frac{T_{v,\text{parcel}} - T_{v,\text{env}}}{T_{v,\text{env}}}\right) - g(q_c + q_r + q_i) - \text{Entraînement}",
        variables={"w": "Vitesse verticale (m/s)", "q_liquid": "Poids des hydrométéores en suspension (kg/kg)"},
        units={"w": "m/s"},
        description="Mouvement ascendant rapide traversant toute la troposphère jusqu'à la tropopause, formant les Cumulonimbus.",
        application_conditions=["CAPE élevé, CIN faible, forçage synoptique ou mésoscale"],
        limitations=["Rôle modérateur du poids des précipitations (water loading) et de l'entraînement"],
        references=["Emanuel (1994) Atmospheric Convection", "AMS Meteorology Glossary"],
    ),
    EncyclopediaEntry(
        key="shallow_convection_process",
        name="Convection Peu Profonde (Shallow Convection)",
        domain="Convection & Orages",
        subdomain="Dynamique convective",
        equation="Convection bloquée sous une inversion de température (ex: alizés)",
        latex_equation=r"\frac{\partial \theta}{\partial t}_{\text{shallow}} = -\frac{1}{\rho}\frac{\partial M_s (\theta - \bar{\theta})}{\partial z}",
        variables={"Ms": "Flux de masse convectif peu profond", "theta": "Température potentielle"},
        units={"Ms": "kg/(m²·s)"},
        description="Convection restreinte aux basses couches (Cumulus humilis/mediocris, alizés) transportant l'humidité sans produire d'orages.",
        application_conditions=["Couche limite convective surmontée d'une couche d'inversion stable"],
        limitations=["Paramétrisation spécifique requise dans les modèles NWP (ex: EDMF)"],
        references=["Tiedtke (1989) Mon. Wea. Rev.", "Météo-France / ECMWF Physics"],
    ),
    EncyclopediaEntry(
        key="updraft_max_velocity",
        name="Courant Ascendant Maximum (Updraft)",
        domain="Convection & Orages",
        subdomain="Cinématique convective",
        equation="w_max = sqrt(2 * CAPE)",
        latex_equation=r"w_{\text{max}} = \sqrt{2 \cdot \text{CAPE}}",
        variables={"CAPE": "J/kg"},
        units={"w_max": "m/s"},
        description="Vitesse verticale théorique maximale d'une parcelle d'air en l'absence de frottement et d'entraînement.",
        application_conditions=["Ascendance adiabatique idéale"],
        limitations=[
            "En pratique, la vitesse réelle est de 30% à 50% de w_max en raison de l'entraînement et du poids de l'eau"
        ],
        references=["Holton & Hakim (2012)", "NOAA SPC Dynamics Manual"],
        compute_func=lambda cape: math.sqrt(2.0 * max(cape, 0.0)),
    ),
    EncyclopediaEntry(
        key="downdraft_cold_pool",
        name="Courant Descendant & Goutte Froide (Downdraft)",
        domain="Convection & Orages",
        subdomain="Cinématique convective",
        equation="w_down = sqrt(2 * DCAPE),  V_gust = C * sqrt(g * dtheta/theta * h)",
        latex_equation=r"w_{\text{down}} = -\sqrt{2 \cdot \text{DCAPE}}, \quad V_{\text{front}} = k \sqrt{g^\prime h}",
        variables={"DCAPE": "Downdraft CAPE (J/kg)", "g_prime": "Gravité réduite g * (delta_theta / theta_0)"},
        units={"w_down": "m/s", "V_front": "m/s"},
        description="Courant descendant froid subsident généré par le refroidissement évaporatif de la pluie et la charge d'eau, créant un front de rafales au sol.",
        application_conditions=["Sous le cœur des précipitations d'un orage"],
        limitations=["Dépend de la sécheresse de la couche sous-nuageuse"],
        references=["Knupp & Cotton (1985)", "Emanuel (1994)"],
        compute_func=compute_downdraft_speed_and_gust_front,
    ),
    EncyclopediaEntry(
        key="entrainment_detrainment_convection",
        name="Entraînement et Détraînement Convectif",
        domain="Convection & Orages",
        subdomain="Paramétrisation du flux de masse",
        equation="dM/dz = (mu - delta) * M",
        latex_equation=r"\frac{1}{M}\frac{dM}{dz} = \epsilon - \delta",
        variables={
            "M": "Flux de masse du courant ascendant (kg/s)",
            "epsilon": "Taux d'entraînement",
            "delta": "Taux de détraînement",
        },
        units={"epsilon, delta": "m⁻¹"},
        description="Mélange turbulent entre le courant ascendant du nuage et l'air environnant. L'entraînement d'air sec affaiblit le courant ascendant.",
        application_conditions=["Modèles de flux de masse convectifs (Tiedtke, Kain-Fritsch, AROME EDMF)"],
        limitations=[
            "Incertitude fondamentale sur la formulation de epsilon en fonction de la flottabilité et du rayon du nuage"
        ],
        references=["Kain & Fritsch (1990) J. Atmos. Sci.", "ECMWF / Météo-France Documentation"],
        compute_func=compute_entrainment_detrainment_mass_flux_gradient,
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
