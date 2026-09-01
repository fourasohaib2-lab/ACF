"""
Advanced Remote Sensing, Satellite Soundings, GPS Radio Occultation & Active Sensors Encyclopedia Module
"""

import math

from acf.science.encyclopedia.entry import EncyclopediaEntry
from acf.science.encyclopedia.registry import EncyclopediaRegistry

# ---------------------------------------------------------------------------
# Computational Functions for Remote Sensing
# ---------------------------------------------------------------------------


def calculate_gps_ro_refractivity(p_hpa: float, temp_k: float, e_hpa: float) -> float:
    """Calcul de la réfractivité atmosphérique GPS Radio Occultation N = 77.6 * (p/T) + 3.73e5 * (e/T^2)."""
    if temp_k <= 0.0:
        return 0.0
    term_dry = 77.6 * (p_hpa / temp_k)
    term_wet = 3.73e5 * (e_hpa / (temp_k**2))
    return term_dry + term_wet


def calculate_radar_zdr(z_h_dbz: float, z_v_dbz: float) -> float:
    """Calcul de la réflectivité différentielle radar ZDR = Zh_dBZ - Zv_dBZ (dB)."""
    return z_h_dbz - z_v_dbz


def calculate_lidar_backscatter_signal(system_constant: float, molecular_backscatter: float, aerosol_backscatter: float, optical_depth: float, range_m: float) -> float:
    """
    Signal de rétrodiffusion lidar (single-scattering lidar equation) :
    P(z) = (C/z^2) * [beta_m(z)+beta_a(z)] * exp(-2*tau(z)), en W.

    NOTE (correction): equation field is fully explicit but this entry
    had no compute_func. Implemented per this entry's OWN more complete
    latex_equation (which includes the 1/z^2 range-dilution term
    universal to any single-scattering range-resolved lidar equation)
    rather than the plain "equation" field's abbreviated summary, which
    omits it - the standard lidar equation always includes 1/z^2 as a
    matter of physical necessity (inverse-square signal dilution with
    range), so it is not optional.
    """
    if range_m <= 0.0:
        raise ValueError("range_m must be positive.")
    return (system_constant / (range_m**2)) * (molecular_backscatter + aerosol_backscatter) * math.exp(-2.0 * optical_depth)


# ---------------------------------------------------------------------------
# Encyclopedia Entries
# ---------------------------------------------------------------------------

ENTRIES: list[EncyclopediaEntry] = [
    EncyclopediaEntry(
        key="gps_radio_occultation_refractivity",
        name="Réfractivité Atmosphérique par Occultation Radio GNSS/GPS (GPS-RO)",
        domain="Télédétection Atmosphérique",
        subdomain="Sondage satellitaire polaire",
        equation="N = (n - 1)*10^6 = 77.6 * (p/T) + 3.73e5 * (e/T^2)",
        latex_equation=r"N = (n - 1)\times 10^6 = 77.6 \frac{p}{T} + 3.73 \times 10^5 \frac{e}{T^2}",
        variables={
            "N": "Réfractivité (unités N)",
            "p": "Pression totale (hPa)",
            "T": "Température (K)",
            "e": "Pression de vapeur d'eau (hPa)",
        },
        units={"N": "N-units"},
        description="Technique d'observation de la Terre mesurant la réfraction des signaux radio des satellites GPS/GNSS traversant l'atmosphère pour restituer des profils verticaux de température et d'humidité à très haute résolution verticale.",
        application_conditions=["Assimilation de données globale dans l'ECMWF IFS, GFS, AROME"],
        limitations=["Résolution horizontale le long de la ligne de visée de l'ordre de 200 km"],
        references=["Kursinski et al. (1997) J. Geophys. Res.", "EUMETSAT ROM SAF Manual", "WMO Satellite Products"],
        compute_func=calculate_gps_ro_refractivity,
    ),
    EncyclopediaEntry(
        key="scatterometer_ocean_surface_winds",
        name="Diffusiométrie Spatiale du Vent de Surface Marine (Scatterometer - ASCAT)",
        domain="Télédétection Atmosphérique",
        subdomain="Capteurs actifs micro-ondes",
        equation="sigma_0 = GMF(U10, phi, theta, pol)  (Geophysical Model Function CMOD5/CMOD7)",
        latex_equation=r"\sigma_0 = \text{GMF}(U_{10}, \phi, \theta, \text{pol})",
        variables={
            "sigma_0": "Section efficace de rétrodiffusion radar (dB)",
            "U10": "Vent équivalent neutre à 10m",
            "phi": "Azimut du vent",
            "GMF": "Fonction de modèle géophysique",
        },
        units={"sigma0": "dB", "U10": "m/s"},
        description="Mesure par radar actif micro-ondes (MetOp ASCAT) du rugosisme capillaire de la surface de l'océan pour déduire la vitesse et la direction du vent de surface marin à 10 m.",
        application_conditions=["Surface de l'océan ouvert (hors de la glace de mer et des zones côtières)"],
        limitations=["Atténuation du signal sous de très fortes précipitations (pluie intense)"],
        references=["Hersbach et al. (2007) J. Geophys. Res. (CMOD5)", "EUMETSAT OSI SAF Manual"],
    ),
    EncyclopediaEntry(
        key="lidar_atmospheric_profiling",
        name="Lidar Atmosphérique Doppler & Rétrodiffusion (Aeolus, CALIPSO)",
        domain="Télédétection Atmosphérique",
        subdomain="Capteurs actifs optiques",
        # NOTE (correction): this plain-text field used to omit the 1/z^2
        # range-dilution term present in this entry's own latex_equation -
        # physically necessary for any single-scattering range-resolved
        # lidar equation, not optional. Now consistent with the latex form.
        equation="Signal de rétrodiffusion P(z) = (C/z^2) * (beta_m(z) + beta_a(z)) * exp(-2*tau(z))",
        latex_equation=r"P(z) = \frac{C}{z^2} \left[\beta_m(z) + \beta_a(z)\right] \exp\left(-2\int_0^z \alpha(z^\prime) dz^\prime\right)",
        variables={
            "beta_m": "Rétrodiffusion moléculaire (Rayleigh)",
            "beta_a": "Rétrodiffusion d'aérosols/nuages (Mie)",
            "alpha": "Coefficient d'extinction",
        },
        units={"P(z)": "W"},
        description="Télédétection optique par laser impulsionnel permettant de mesurer le profil vertical du vent (Lidar Doppler ALADIN sur ESA Aeolus) et la structure verticale des nuages et aérosols (CALIPSO/EarthCARE).",
        application_conditions=["Profils verticaux du vent et des aérosols en ciel clair ou nuages optiquement fins"],
        limitations=["Atténuation complète du faisceau laser par les nuages opaques (épaisses couvertures nuageuses)"],
        references=["ESA Aeolus Mission Reports", "Winker et al. (2009) CALIPSO J. Atmos. Oceanic Technol."],
        compute_func=calculate_lidar_backscatter_signal,
    ),
    EncyclopediaEntry(
        key="polarimetric_radar_zdr",
        name="Réflectivité Différentielle Radar (ZDR)",
        domain="Télédétection Atmosphérique",
        subdomain="Radar météorologique double polarisation",
        equation="ZDR = Zh_dBZ - Zv_dBZ = 10 * log10(Zh / Zv)",
        latex_equation=r"Z_{\text{DR}} = 10 \log_{10}\left(\frac{Z_H}{Z_V}\right) = Z_{H,\text{dBZ}} - Z_{V,\text{dBZ}}",
        variables={"ZH": "Réflectivité en polarisation horizontale", "ZV": "Réflectivité en polarisation verticale"},
        units={"ZDR": "dB"},
        description="Rapport sans dimension mesurant l'oblatié moyenne des hydrométéores. ZDR > 0 caractérise les grosses gouttes d'pluie aplaties, ZDR ~ 0 caractérise les grêlons sphériques.",
        application_conditions=["Radars météo à double polarisation (C-band, S-band, X-band)"],
        limitations=["Requiert une calibration électronique matérielle exacte (< 0.1 dB)"],
        references=[
            "Bringi & Chandrasekar (2001) Polarimetric Radar Meteorology",
            "NOAA / Météo-France Dual-Pol Manuals",
        ],
        compute_func=calculate_radar_zdr,
    ),
]

for entry in ENTRIES:
    EncyclopediaRegistry.register(entry)
