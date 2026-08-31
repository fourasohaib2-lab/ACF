"""
Atmospheric Complexity Framework (ACF)

Global Physical Oceanography & Ocean Database Module (Phase 1)
(SST, SSS, MLD, Brunt-Väisälä Frequency N², Ekman Pumping, Geostrophic Currents, AMOC)
"""

import math
from typing import Any


class PhysicalOceanographyEngine:
    """
    Moteur de dynamique océanique physique et d'équations hydrodynamiques marines.
    """

    @staticmethod
    def brunt_vaisala_frequency(d_rho_dz: float, rho_0: float = 1025.0) -> float:
        """Calcul de la fréquence de Brunt-Väisälä N² = - (g / rho_0) * (d_rho / dz)."""
        g = 9.80665
        n2 = -(g / rho_0) * d_rho_dz
        return max(0.0, n2)

    @staticmethod
    def ekman_pumping_velocity(curl_tau: float, latitude_deg: float, rho_0: float = 1025.0) -> float:
        """Calcul de la vitesse de pompage d'Ekman w_e = (1 / (rho_0 * f)) * (rot tau) (m/s)."""
        omega = 7.292115e-5
        f = 2.0 * omega * math.sin(math.radians(latitude_deg))
        if abs(f) < 1e-6:
            return 0.0
        return curl_tau / (rho_0 * f)

    @staticmethod
    def geostrophic_current_velocity(dp_dx: float, latitude_deg: float, rho_0: float = 1025.0) -> float:
        """Calcul de la vitesse du courant géostrophique v_g = (1 / (rho_0 * f)) * (dp / dx)."""
        omega = 7.292115e-5
        f = 2.0 * omega * math.sin(math.radians(latitude_deg))
        if abs(f) < 1e-6:
            return 0.0
        return dp_dx / (rho_0 * f)


class OceanDatabase:
    """Base de données et registre des grandes masses d'eau et bassins océaniques mondiaux."""

    @classmethod
    def get_ocean_basin_info(cls, basin_name: str) -> dict[str, Any]:
        b = basin_name.lower()
        if "atlantique" in b or "atlantic" in b:
            return {
                "name": "Bassin Atlantique Nord",
                "currents": ["Gulf Stream", "North Atlantic Drift", "Canary Current", "Labrador Current"],
                "amoc_status": "Overturning circulation strength ~17 Sv",
                "avg_sst_c": 18.5,
                "avg_sss_psu": 35.5,
            }
        return {
            "name": "Bassin Pacifique",
            "currents": ["Kuroshio", "California Current", "Equatorial Countercurrent"],
            "avg_sst_c": 21.0,
            "avg_sss_psu": 34.8,
        }
