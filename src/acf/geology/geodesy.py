"""
Atmospheric Complexity Framework (ACF)

Geodesy, GNSS & InSAR Crustal Deformation Engine Module (Phase 11)
(GNSS Station Displacement, InSAR Line-Of-Sight Phase Shift, Tectonic Strain Rate)
"""

import math
from typing import Any, Dict


class GeodesyEngine:
    """
    Moteur de mesures géodésiques de déformation crustale (GNSS / InSAR / VLBI).
    """

    @staticmethod
    def insar_phase_to_displacement_mm(phase_shift_rad: float, wavelength_cm: float = 5.55) -> float:
        """
        Convertit un déphasage InSAR (radar Sentinel-1 bande C lambda = 5.55 cm) en déplacement LOS (mm).
        d = (lambda / (4 * pi)) * delta_phi.
        """
        d_cm = (wavelength_cm / (4.0 * math.pi)) * phase_shift_rad
        return d_cm * 10.0  # en mm

    @classmethod
    def gnss_displacement_vector(cls, station_id: str, ve_mm_yr: float, vn_mm_yr: float, vu_mm_yr: float) -> Dict[str, Any]:
        """Calcule le vecteur de vitesse horizontal et vertical d'une station GNSS."""
        v_horiz = math.sqrt(ve_mm_yr**2 + vn_mm_yr**2)
        azimuth = math.degrees(math.atan2(ve_mm_yr, vn_mm_yr)) % 360.0

        return {
            "station_id": station_id,
            "horizontal_velocity_mm_yr": round(v_horiz, 2),
            "azimuth_deg": round(azimuth, 1),
            "vertical_uplift_mm_yr": round(vu_mm_yr, 2),
        }
