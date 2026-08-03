"""
Atmospheric Chemistry, Photochemistry, Aerosols, Air Quality & Deposition Encyclopedia Module
"""

from typing import List
from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

# ---------------------------------------------------------------------------
# Computational Functions for Atmospheric Chemistry
# ---------------------------------------------------------------------------

def calculate_leighton_ozone_photoequilibrium(j_no2: float, no2_ppb: float, no_ppb: float, k_o3_no: float = 1.8e-14) -> float:
    """Calcul de la concentration d'ozone à l'état photostationnaire de Leighton [O3] = (j_NO2 * [NO2]) / (k * [NO])."""
    if no_ppb <= 0.0 or k_o3_no <= 0.0:
        return 0.0
    return (j_no2 * no2_ppb) / (k_o3_no * no_ppb)


def calculate_dry_deposition_velocity(ra_s_m: float, rb_s_m: float, rc_s_m: float) -> float:
    """Calcul de la vitesse de dépôt sec vd = 1 / (Ra + Rb + Rc) en m/s."""
    r_total = ra_s_m + rb_s_m + rc_s_m
    if r_total <= 0.0:
        return 0.0
    return 1.0 / r_total


# ---------------------------------------------------------------------------
# Encyclopedia Entries
# ---------------------------------------------------------------------------

ENTRIES: List[EncyclopediaEntry] = [
    EncyclopediaEntry(
        key="leighton_photoequilibrium_ozone",
        name="Relation de Photostationnarité de Leighton (Ozone Troposphérique)",
        domain="Chimie Atmosphérique",
        subdomain="Photochimie troposphérique",
        equation="[O3] = (j_NO2 * [NO2]) / (k_O3+NO * [NO])",
        latex_equation=r"[\text{O}_3] = \frac{j_{\text{NO}_2} [\text{NO}_2]}{k_{\text{O}_3+\text{NO}} [\text{NO}]}",
        variables={"j_NO2": "Taux de photolyse du NO2 (s⁻¹)", "k_O3+NO": "Constante de réaction NO + O3 -> NO2 + O2", "[NO2], [NO]": "Concentrations des oxydes d'azote"},
        units={"[O3]": "ppb"},
        description="Équilibre photostationnaire rapide gouvernant les concentrations d'ozone, de monoxyde d'azote et de dioxyde d'azote dans la troposphère non polluée en journée.",
        application_conditions=["Troposphère diurne sous rayonnement solaire UV en l'absence de COV réactifs massifs"],
        limitations=["Violée en présence de radicaux péroxydes (RO2/HO2) issus de la dégradation des COV (formation de smog)"],
        references=["Leighton (1961) Photochemistry of Air Pollution", "Seinfeld & Pandis (2016) Atmospheric Chemistry"],
        compute_func=calculate_leighton_ozone_photoequilibrium,
    ),
    EncyclopediaEntry(
        key="particulate_matter_pm25_pm10",
        name="Particules en Suspension PM2.5 et PM10 (Air Quality)",
        domain="Chimie Atmosphérique",
        subdomain="Qualité de l'air & Aérosols",
        equation="Concentration massique des particules de diamètre aérodynamique < 2.5 µm (PM2.5) et < 10 µm (PM10)",
        latex_equation=r"\text{PM}_{2.5} = \int_0^{2.5\mu\text{m}} \frac{\pi}{6} \rho_p D^3 N(D) dD",
        variables={"PM2.5": "Masse volumique des particules fines (µg/m³)", "rho_p": "Masse volumique des particules"},
        units={"PM": "µg/m³"},
        description="Indicateurs réglementaires majeurs de la pollution de l'air. Les PM2.5 s'infiltrent profondément dans les alvéoles pulmonaires et le système sanguin.",
        application_conditions=["Modèles de chimie-transport (CTM ex: CHIMERE, MOCAGE, CAMS) et santé publique"],
        limitations=["Les limites de concentration recommandées par l'OMS sont de 5 µg/m³ en moyenne annuelle pour les PM2.5"],
        references=["WHO Air Quality Guidelines (2021)", "Seinfeld & Pandis (2016)"],
    ),
    EncyclopediaEntry(
        key="dry_wet_deposition_mechanisms",
        name="Dépôt Sec et Scavenging Humide des Aérosols",
        domain="Chimie Atmosphérique",
        subdomain="Transport et élimination",
        equation="Dépôt sec: F_dry = v_d * C  ;  Dépôt humide: S = Lambda_scav * C",
        latex_equation=r"v_d = \frac{1}{R_a + R_b + R_c}, \quad \left.\frac{\partial C}{\partial t}\right|_{\text{humide}} = -\Lambda_{\text{scav}} C",
        variables={"vd": "Vitesse de dépôt sec (m/s)", "Ra": "Résistance aérodynamique", "Rb": "Résistance de couche limite quasi-laminaire", "Rc": "Résistance stomatique/surface", "Lambda": "Coefficient de lessivage par la pluie"},
        units={"vd": "m/s", "Lambda": "s⁻¹"},
        description="Processus de nettoyage naturel de l'atmosphère retirant les gaz réactifs et aérosols par sédimentation/capture de surface (dépôt sec) ou par impaction/capture par les gouttes d'eau et cristaux (lessivage humide).",
        application_conditions=["Modélisation de la qualité de l'air, pluies acides et transport de suies/poussières"],
        limitations=["La résistance stomatique Rc dépend fortement de l'état physiologique de la végétation"],
        references=["Wesely (1989) Atmos. Environ.", "Seinfeld & Pandis (2016)"],
        compute_func=calculate_dry_deposition_velocity,
    ),
    EncyclopediaEntry(
        key="aerosol_optical_depth_aod",
        name="Épaisseur Optique des Aérosols (AOD / AOT)",
        domain="Chimie Atmosphérique",
        subdomain="Propriétés optiques des aérosols",
        equation="AOD(lambda) = int_0^z_top alpha_ext(z, lambda) dz",
        latex_equation=r"\tau(\lambda) = \int_0^{\infty} \alpha_{\text{ext}}(z, \lambda) dz = \int_0^{\infty} \sigma_{\text{ext}}(\lambda, r) N(z, r) dr dz",
        variables={"tau": "Épaisseur optique adimensionnelle", "alpha_ext": "Coefficient d'extinction massique (m⁻¹)"},
        units={"AOD": "dimensionless"},
        description="Intégrale verticale du coefficient d'extinction (absorption + diffusion) causé par les aérosols. Mesurée par les radiomètres solaires AERONET et les satellites MODIS/VIIRS.",
        application_conditions=["Bilan radiatif terrestre et restitution de la qualité de l'air par satellite"],
        limitations=["Dépendance spectrale forte décrite par l'exposant d'Ångström alpha"],
        references=["Holben et al. (1998) Remote Sens. Environ. (AERONET)", "Liou (2002)"],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
