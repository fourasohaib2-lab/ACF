"""
Radar Meteorology, Dual Polarization, Velocity Dealiasing & Hydrometeor Classification Encyclopedia Module
"""

from typing import List
from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

# ---------------------------------------------------------------------------
# Computational Functions for Radar Meteorology
# ---------------------------------------------------------------------------

def calculate_specific_differential_phase_kdp(phidp_far_deg: float, phidp_near_deg: float, distance_km: float) -> float:
    """Calcul de la phase différentielle spécifique KDP = 0.5 * (PhiDP_far - PhiDP_near) / dr (deg/km)."""
    if distance_km <= 0.0:
        return 0.0
    return 0.5 * (phidp_far_deg - phidp_near_deg) / distance_km


def calculate_rain_rate_zr_marshall_palmer(zh_linear: float, a: float = 200.0, b: float = 1.6) -> float:
    """Calcul du taux de pluie Z-R de Marshall-Palmer Z = a * R^b -> R = (Z / a)^(1 / b) en mm/h."""
    if zh_linear <= 0.0:
        return 0.0
    return (zh_linear / a) ** (1.0 / b)


# ---------------------------------------------------------------------------
# Encyclopedia Entries
# ---------------------------------------------------------------------------

ENTRIES: List[EncyclopediaEntry] = [
    EncyclopediaEntry(
        key="radar_specific_differential_phase_kdp",
        name="Phase Différentielle Spécifique Radar (KDP)",
        domain="Télédétection Radar",
        subdomain="Radar double polarisation",
        equation="KDP = 0.5 * d(PhiDP) / dr  (deg/km)",
        latex_equation=r"K_{\text{DP}} = \frac{1}{2} \frac{\partial \Phi_{\text{DP}}}{\partial r}",
        variables={"PhiDP": "Déphasage d'onde entre polarisation H et V (degrés)", "r": "Distance au radar (km)"},
        units={"KDP": "deg/km"},
        description="Mesure de la différence de changement de phase de propagation entre les polarisations H et V. KDP est insensible à l'atténuation par la pluie et aux erreurs de calibration du radar.",
        application_conditions=["Estimation radar des précipitations intenses (QPE) et identification des zones de forte pluie"],
        limitations=["Nécessite le filtrage du bruit de phase sur la variable brute PhiDP"],
        references=["Bringi & Chandrasekar (2001) Polarimetric Radar Meteorology", "NOAA NSSL Dual-Pol Manual"],
        compute_func=calculate_specific_differential_phase_kdp,
    ),
    EncyclopediaEntry(
        key="hydrometeor_classification_algorithm_hca",
        name="Algorithme de Classification des Hydrométéores (HCA Radar)",
        domain="Télédétection Radar",
        subdomain="Traitement de signal radar",
        equation="Logique floue (Fuzzy Logic): Membership = f(Z_H, Z_DR, K_DP, rho_hv, T)",
        latex_equation=r"P(\text{Class}_i) = \frac{\sum w_j \mu_{ij}(x_j)}{\sum w_j}",
        variables={"x_j": "Variables polaires (ZH, ZDR, KDP, rho_hv, Température)", "mu_ij": "Fonctions d'appartenance"},
        units={"Classification": "Classes (Pluie, Glace, Neige, Graupel, Grêle, Insectes, Parasites)"},
        description="Algorithme à logique floue permettant de classer automatiquement à chaque porte d'aéronef le type d'hydrométéore rencontré dans le nuage.",
        application_conditions=["Radars météo opérationnels (NOAA NEXRAD, Météo-France PANTHERE, DWD)"],
        limitations=["Précision dépendante de la hauteur de l'isotherme 0°C fournie par les modèles NWP"],
        references=["Park et al. (2009) J. Appl. Meteor. Climatol.", "Ryzhkov et al. (2005)"],
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
