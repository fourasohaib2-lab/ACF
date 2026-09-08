"""
Atmospheric Complexity Framework (ACF)

Volcanic Physics, Mogi Deformation Model & Plume Dynamics Module (Phase 8)
(Mogi Inflation Model Dz = 3*dV*d / (4*pi*(r² + d²)^(3/2)), Volcanic Plume Height H, Lahars)
"""

import math


class VolcanicPhysicsEngine:
    """
    Moteur de physique volcanique (Déformation par chambre magmatique Mogi, dynamique du panache).
    """

    @staticmethod
    def mogi_surface_displacement_m(
        radial_distance_m: float, chamber_depth_m: float, volume_change_m3: float, poisson_ratio: float = 0.25
    ) -> dict[str, float]:
        """
        Modèle de déformation élastique de Mogi (1958) pour une chambre magmatique sphérique.
        Dz = ((1 - nu) / pi) * dV * d / (r² + d²)^(3/2) (déplacement vertical).
        Dr = ((1 - nu) / pi) * dV * r / (r² + d²)^(3/2) (déplacement radial).
        """
        r2_d2 = (radial_distance_m**2) + (chamber_depth_m**2)
        denom = r2_d2**1.5

        if denom <= 0:
            return {"vertical_displacement_m": 0.0, "radial_displacement_m": 0.0}

        factor = ((1.0 - poisson_ratio) / math.pi) * volume_change_m3

        dz = factor * (chamber_depth_m / denom)
        dr = factor * (radial_distance_m / denom)

        return {
            "vertical_displacement_m": round(dz, 4),
            "radial_displacement_m": round(dr, 4),
        }

    @staticmethod
    def volcanic_plume_height_km(volumetric_eruption_rate_m3_s: float) -> float:
        """
        Calcul de la hauteur maximale du panache éruptif H = 2.0 * (V_rate)^0.241 (Mastin et al., 2009).
        """
        if volumetric_eruption_rate_m3_s <= 0:
            return 0.0
        return 2.0 * (volumetric_eruption_rate_m3_s**0.241)
