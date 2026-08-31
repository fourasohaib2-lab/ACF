"""
Atmospheric Complexity Framework (ACF)

Lightning Physics, Cloud Electrification & Transient Luminous Events Encyclopedia Module
"""

import math

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

# ---------------------------------------------------------------------------
# Computational Functions for Lightning & Electrification
# ---------------------------------------------------------------------------


def calculate_price_rind_flash_rate(cloud_top_height_km: float, is_marine: bool = False) -> float:
    """Calcul de la fréquence totale des éclairs (éclairs / min) d'après Price & Rind (1992)."""
    if cloud_top_height_km <= 0.0:
        return 0.0
    if is_marine:
        return 6.2e-4 * (cloud_top_height_km**1.73)
    return 3.44e-5 * (cloud_top_height_km**4.9)


def calculate_mccaul_graupel_lightning_index(graupel_flux: float, ice_flux: float, cape: float) -> float:
    """Estimation du taux d'éclairs basée sur le produit du flux de graupel et de glace dans la zone de surenfusion."""
    if cape <= 0.0:
        return 0.0
    return 0.05 * math.sqrt(cape) * (graupel_flux * ice_flux) ** 0.5


# ---------------------------------------------------------------------------
# Encyclopedia Entries
# ---------------------------------------------------------------------------

ENTRIES: list[EncyclopediaEntry] = [
    EncyclopediaEntry(
        key="non_inductive_cloud_charging",
        name="Électrification Non-Inductive par Collision Glace-Graupel",
        domain="Foudre & Électricité Atmosphérique",
        subdomain="Physique de l'orage",
        equation="delta_q = f(T, LWC, v_rel)",
        latex_equation=r"\Delta q = q_{\text{graupel}} - q_{\text{crystal}} \propto f(T, \text{LWC}, V_{\text{rel}})",
        variables={"T": "Température zone de givrage (-10 à -20°C)", "LWC": "Contenu en eau liquide (g/m³)"},
        units={"delta_q": "pC par collision"},
        description="Transfert de charge électrique lors du choc entre des cristaux de glace légers (se chargeant positivement) et des graupels plus lourds (se chargeant négativement).",
        application_conditions=["Zone de coexistence eau surfondue / glace / graupel entre -10°C et -20°C"],
        limitations=["Inversion du signe de charge à la température de déflexion Tr (~ -15°C)"],
        references=["Takahashi (1978) J. Atmos. Sci.", "Saunders et al. (1991)", "WMO Lightning Physics Manual"],
        compute_func=lambda temp_c, lwc: 0.1 * (temp_c + 15.0) * lwc if -25.0 <= temp_c <= -5.0 else 0.0,
    ),
    EncyclopediaEntry(
        key="graupel_ice_collision_charging",
        name="Séparation de Charge Glace-Graupel",
        domain="Foudre & Électricité Atmosphérique",
        subdomain="Microphysique de la foudre",
        equation="J_charge = N_graupel * N_ice * CrossSection * V_rel * delta_q",
        latex_equation=r"J_{\text{charge}} = \int \int N_g(D_g) N_i(D_i) A_{gi} |V_g - V_i| \Delta q \, dD_g \, dD_i",
        variables={"Ng, Ni": "Concentrations graupel et glace (m⁻³)", "Vg, Vi": "Vitesses de chute (m/s)"},
        units={"J_charge": "C/(m³·s)"},
        description="Densité de courant de charge générée au cœur du courant ascendant d'un Cumulonimbus.",
        application_conditions=["Noyau convectif au-dessus de l'isotherme 0°C"],
        limitations=["Modélisation dépendant de la précision du schéma microphysique"],
        references=["Deierling et al. (2008) J. Geophys. Res.", "AMS Lightning Physics"],
    ),
    EncyclopediaEntry(
        key="cloud_tripole_structure",
        name="Structure Tri-polaire du Cumulonimbus",
        domain="Foudre & Électricité Atmosphérique",
        subdomain="Électricité atmosphérique",
        equation="Q_upper(+) [10-12km], Q_main(-) [6-8km], Q_lower(+) [2-4km]",
        latex_equation=r"\rho_e(z) = Q_+ \delta(z - z_u) - Q_- \delta(z - z_m) + q_+ \delta(z - z_l)",
        variables={
            "Q_upper": "Centre de charge positive supérieur (sommet glacé)",
            "Q_main": "Centre de charge négative principal (-15°C)",
            "Q_lower": "Poche positive inférieure (base chaud/pluie)",
        },
        units={"Q": "Coulombs (C)"},
        description="Distribution verticale canonique des charges électriques au sein d'un orage créant un champ électrique de plusieurs centaines de kV/m.",
        application_conditions=["Orages à maturité"],
        limitations=["Formations complexes multipolaires dans les supercellules"],
        references=["Williams (1989) J. Geophys. Res.", "NOAA NSSL Electrification Manual"],
    ),
    EncyclopediaEntry(
        key="cloud_to_ground_lightning_cg",
        name="Éclair Sol-Nuage (Cloud-to-Ground Lightning CG)",
        domain="Foudre & Électricité Atmosphérique",
        subdomain="Décharges électriques",
        equation="I_peak = 30 to 100 kA, V_breakdown > 3 MV/m",
        latex_equation=r"E_{\text{breakdown}} \ge 3 \times 10^6 \text{ V/m}, \quad I_{\text{return}} \approx 30 \text{ kA}",
        variables={
            "I_peak": "Intensité de crête du coup en retour (kA)",
            "E_breakdown": "Champ de claquage dielectrique (V/m)",
        },
        units={"I": "kA", "E": "V/m"},
        description="Décharge électrique entre le centre de charge négatif (ou positif) du nuage et la surface du sol initiée par un tracé précurseur (stepped leader).",
        application_conditions=["Réseaux de détection foudre au sol (VLF/LF, Météorage, NLDN)"],
        limitations=["CG négatifs (90%) vs CG positifs (10%, plus destructeurs)"],
        references=["Rakov & Uman (2003) Lightning: Physics and Effects", "WMO Guide"],
    ),
    EncyclopediaEntry(
        key="intra_cloud_lightning_ic",
        name="Éclair Intra-Nuage (Intra-Cloud Lightning IC)",
        domain="Foudre & Électricité Atmosphérique",
        subdomain="Décharges électriques",
        equation="Ratio IC/CG = 3:1 to 10:1 (fonction de la latitude)",
        latex_equation=r"\frac{N_{\text{IC}}}{N_{\text{CG}}} \propto f(\text{Latitude}, \text{CAPE})",
        variables={"NIC": "Nombre d'éclairs intra-nuage", "NCG": "Nombre d'éclairs nuage-sol"},
        units={"Ratio": "dimensionless"},
        description="Décharge électrique se produisant entièrement à l'intérieur du nuage entre les centres de charges opposées (représente 70 à 90% du total des éclairs).",
        application_conditions=["Détection satellitaire (GOES GLM, MTG LI) et VHF LMA"],
        limitations=["Moins dangereux au sol mais précurseur des rafales violentes et tornades (jump de foudre)"],
        references=["MacGorman & Rust (1998)", "NASA GLM ATBD Document"],
    ),
    EncyclopediaEntry(
        key="lightning_flash_rate_price_rind",
        name="Paramétrisation du Taux d'Éclairs (Price & Rind)",
        domain="Foudre & Électricité Atmosphérique",
        subdomain="Paramétrisation NWP",
        equation="F_continental = 3.44e-5 * H_top^4.9",
        latex_equation=r"F_{\text{flash}} = 3.44 \times 10^{-5} H_{\text{top}}^{4.9}",
        variables={"Htop": "Hauteur du sommet du Cumulonimbus (km)"},
        units={"F_flash": "éclairs / min"},
        description="Relation puissance reliant la hauteur de la tour convective d'un Cumulonimbus à la fréquence de la foudre.",
        application_conditions=["Convection profonde continentale / maritime"],
        limitations=["Fréquence 5 fois plus faible sur océan à hauteur égale"],
        references=["Price & Rind (1992) Geophys. Res. Lett.", "ECMWF / WMO Documentation"],
        compute_func=calculate_price_rind_flash_rate,
    ),
    EncyclopediaEntry(
        key="mccaul_lightning_threat_index",
        name="Indice de Menace de Foudre (McCaul / WRF)",
        domain="Foudre & Électricité Atmosphérique",
        subdomain="Paramétrisation NWP",
        equation="LTI = C1 * w_max * Q_graupel + C2 * Vert_Integrated_Ice",
        latex_equation=r"\text{LTI} = k_1 w_{\text{max}} q_{g,-15°C} + k_2 \int \rho q_i \, dz",
        variables={"w_max": "Vitesse verticale max dans la zone glacée", "qg": "Graupel à -15°C"},
        units={"LTI": "éclairs / (km²·min)"},
        description="Indice de menace de foudre explicite utilisé dans le modèle WRF combinant le flux de graupel et le contenu intégré en glace.",
        application_conditions=["Modèles NWP méso-échelle à résolution explicite"],
        limitations=["Sensible à la microphysique de glace"],
        references=["McCaul et al. (2009) Wea. Forecasting", "NCAR WRF Manual"],
        compute_func=calculate_mccaul_graupel_lightning_index,
    ),
    # ---------------------------------------------------------------------------
    # TLE: Sprites & ELVES
    # ---------------------------------------------------------------------------
    EncyclopediaEntry(
        key="sprites_tles_mesosphere",
        name="Sprites (Phénomènes Lumineux Transitoires - TLE)",
        domain="Foudre & Électricité Atmosphérique",
        subdomain="Phénomènes haute atmosphère",
        equation="Altitude 50 - 90 km (Mésosphère), excitation par décharge +CG à fort moment de charge",
        latex_equation=r"i_{\text{sprite}} \propto Q_{\text{change}} \cdot h_{\text{cloud}} > 300 \text{ C}\cdot\text{km}",
        variables={"Q_change": "Charge transférée par le +CG au sol", "Altitude": "50-90 km"},
        units={"Couleur": "Rouge (N2 excitation)", "Moment": "C·km"},
        description="Décharges électriques lumineuses rouges se produisant dans la mésosphère au-dessus des grands orages (MCS) suite à un éclair sol-nuage positif massif (+CG).",
        application_conditions=["Au-dessus des stratiformes des MCS"],
        limitations=["Nécessite un moment de charge neutralisé extrêmement élevé (> 300 C·km)"],
        references=["Sentman et al. (1995) Geophys. Res. Lett.", "NASA / ESA TLE Research"],
    ),
    EncyclopediaEntry(
        key="elves_tles_ionosphere",
        name="ELVES (Emissions of Light and VLF Perturbations)",
        domain="Foudre & Électricité Atmosphérique",
        subdomain="Phénomènes haute atmosphère",
        equation="Altitude 80 - 100 km (Ionosphère), expansion de l'impulsion électromagnétique (EMP)",
        latex_equation=r"R_{\text{elves}} = c \sqrt{t^2 + 2 t \frac{h}{c}} \quad (\text{Anneau de lumière rapide < 1 ms})",
        variables={"h": "Altitude ionosphérique (90 km)", "t": "Temps depuis l'impulsion EMP"},
        units={"Durée": "< 1 ms", "Rayon": "jusqu'à 500 km"},
        description="Disques ou anneaux de lumière ultra-rapides se propageant dans la basse ionosphère sous l'effet de l'impulsion électromagnétique intense émise par un éclair de forte intensité.",
        application_conditions=["Base de l'ionosphère à 90 km"],
        limitations=[
            "Durée inférieure à la milliseconde, visible uniquement avec des caméras ultrarapides ou satellites"
        ],
        references=["Inan et al. (1997) Geophys. Res. Lett.", "AMS High-Atmosphere Electrodynamics"],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
