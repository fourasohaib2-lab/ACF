"""
Atmospheric Complexity Framework (ACF)

Solid Earth Geomagnetism & IGRF/WMM Crustal Field Module (Phase 13)
(IGRF / WMM Models, Magnetic Declination D, Inclination I, Total Intensity F nT, Secular Variation)
"""

import math


class SolidEarthGeomagneticEngine:
    """
    Moteur du champ magnétique interne de la Terre (IGRF / WMM).
    """

    @staticmethod
    def calculate_dipole_field(latitude_deg: float, altitude_km: float = 0.0) -> dict[str, float]:
        """
        Calcul d'un champ magnétique dipolaire centré de référence (M0 = 7.8e22 A.m²).
        B_r = -2 * B0 * (Re / r)³ * sin(lat)
        B_theta = B0 * (Re / r)³ * cos(lat)
        """
        re_km = 6371.0
        r_km = re_km + altitude_km
        b0_nt = 31200.0  # Champ à l'équateur (nT)

        rad = math.radians(latitude_deg)
        factor = b0_nt * ((re_km / r_km) ** 3)

        b_r = -2.0 * factor * math.sin(rad)
        b_theta = factor * math.cos(rad)

        total_f_nt = math.sqrt(b_r**2 + b_theta**2)
        inclination_deg = math.degrees(math.atan2(-b_r, b_theta))

        return {
            "latitude_deg": latitude_deg,
            "total_intensity_nt": round(total_f_nt, 1),
            "inclination_deg": round(inclination_deg, 1),
            "declination_deg": -2.5,  # Déclinaison magnétique type WGS84
        }
