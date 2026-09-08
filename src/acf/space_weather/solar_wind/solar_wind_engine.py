"""
Atmospheric Complexity Framework (ACF)

Solar Wind Hydrodynamics & Interplanetary Magnetic Field Module (Phase 2)
(Parker Spiral, Solar Wind Speed Vsw, Dynamic Pressure Pdyn, IMF Bx/By/Bz, Clock Angle, Reconnection)
"""

import math
from dataclasses import dataclass
from typing import Any


@dataclass
class InterplanetaryMagneticField:
    """Composantes vectorielles du Champ Magnétique Interplanétaire (IMF) en nT."""

    bx_nt: float
    by_nt: float
    bz_nt: float
    total_b_nt: float

    @property
    def clock_angle_deg(self) -> float:
        """Calcul de l'angle d'horloge de l'IMF theta = arctan2(By, Bz) en degrés (0° à 360°)."""
        angle = math.degrees(math.atan2(self.by_nt, self.bz_nt))
        return angle % 360.0


class SolarWindEngine:
    """Moteur hydrodynamique du vent solaire et de propagation de la spirale de Parker."""

    @staticmethod
    def dynamic_pressure_npa(solar_wind_speed_km_s: float, proton_density_cm3: float) -> float:
        """Calcul de la pression dynamique du vent solaire Pdyn = m_p * N * V² (en nPa)."""
        m_p_kg = 1.67262e-27
        n_m3 = proton_density_cm3 * 1e6
        v_m_s = solar_wind_speed_km_s * 1000.0

        pdyn_pa = m_p_kg * n_m3 * (v_m_s**2)
        return pdyn_pa * 1e9  # Conversion en nanoPascals (nPa)

    @staticmethod
    def parker_spiral_longitude_deg(distance_au: float, solar_wind_speed_km_s: float) -> float:
        """
        Calcul de l'angle "garden-hose" (tuyau d'arrosage) de la spirale de Parker :
        psi = arctan(omega * r / Vsw). omega = 2.865e-6 rad/s (rotation solaire).

        NOTE (correction): omega*r/Vsw is tan(psi), a dimensionless
        ratio - not an angle in radians. This used to feed that ratio
        straight into math.degrees() without ever taking arctan() of
        it, i.e. it implicitly used the small-angle approximation
        tan(x) ~= x, which is nowhere close to valid at these values
        (the ratio is ~1.07 at 1 AU / 400 km/s, not small). That gave
        ~61° at 1 AU instead of the correct, textbook ~45° garden-hose
        angle, and grew past the formula's own asymptotic 90° limit at
        larger heliocentric distances (e.g. ~307° at 5 AU, an
        impossible angle) instead of approaching it.
        """
        omega = 2.865e-6
        r_m = distance_au * 1.496e11
        v_m_s = solar_wind_speed_km_s * 1000.0

        tan_psi = (omega * r_m) / v_m_s
        return math.degrees(math.atan(tan_psi))

    @classmethod
    def evaluate_reconnection_risk(cls, imf: InterplanetaryMagneticField) -> dict[str, Any]:
        """Évalue la probabilité de reconnexion magnétique à la magnétopause (B_z négatif / Sud)."""
        if imf.bz_nt < -10.0:
            risk = "CRITICAL / STRONG MAGNETIC RECONNECTION"
            reconnection_factor = min(1.0, abs(imf.bz_nt) / 20.0)
        elif imf.bz_nt < 0.0:
            risk = "MODERATE / SOUTHWARD BZ"
            reconnection_factor = abs(imf.bz_nt) / 20.0
        else:
            risk = "LOW / NORTHWARD BZ"
            reconnection_factor = 0.0

        return {
            "imf_bz_nt": imf.bz_nt,
            "clock_angle_deg": round(imf.clock_angle_deg, 1),
            "reconnection_risk": risk,
            "reconnection_efficiency": round(reconnection_factor, 2),
        }
