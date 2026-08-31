"""
Observation Forward Operators H(x) Module for Data Assimilation
"""

import math


def observe_temperature_2m(surface_temp_k: float, lapse_rate_k_m: float = 0.0065, height_m: float = 2.0) -> float:
    """Opérateur d'observation H(x) pour la température à 2 mètres."""
    return surface_temp_k - lapse_rate_k_m * height_m


def observe_radar_reflectivity_zh(q_r_kg_kg: float, rho_air_kg_m3: float = 1.2) -> float:
    """
    Opérateur d'observation H(x) pour la réflectivité radar horizontale Z_H (dBZ)
    basé sur la relation Z = 2.4e4 * (rho * q_r)^1.75.
    """
    if q_r_kg_kg <= 0.0:
        return -30.0  # Fond du bruit
    lwc_g_m3 = q_r_kg_kg * rho_air_kg_m3 * 1000.0
    z_linear = 24000.0 * (lwc_g_m3**1.75)
    return 10.0 * math.log10(max(z_linear, 1e-3))


def observe_radar_doppler_radial_velocity(
    u_ms: float, v_ms: float, w_ms: float, azimuth_deg: float, elevation_deg: float
) -> float:
    """
    Opérateur d'observation H(x) pour la vitesse radiale Doppler V_r (positif s'éloignant du radar).
    V_r = u * sin(az) * cos(el) + v * cos(az) * cos(el) + w * sin(el).
    """
    az_rad = math.radians(azimuth_deg)
    el_rad = math.radians(elevation_deg)
    return (
        u_ms * math.sin(az_rad) * math.cos(el_rad)
        + v_ms * math.cos(az_rad) * math.cos(el_rad)
        + w_ms * math.sin(el_rad)
    )


def observe_gnss_zenith_wet_delay_zwd(pwv_mm: float, pi_factor: float = 0.15) -> float:
    """Opérateur d'observation H(x) du délai humide au zénith ZWD = PWV / PI (mètres)."""
    if pwv_mm <= 0.0 or pi_factor <= 0.0:
        return 0.0
    return (pwv_mm / 1000.0) / pi_factor
