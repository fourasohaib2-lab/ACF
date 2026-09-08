"""
Atmospheric Complexity Framework (ACF)

Impact Tsunami Hydrodynamics Engine Module (Phase 4)
(ImpactTsunamiEngine calculating initial ocean wave height, propagation, and Green's law coastal amplification)
"""

import math
from typing import Any

GRAVITY_EARTH = 9.80665  # m/s^2


class ImpactTsunamiEngine:
    """
    Moteur de simulation des tsunamis générés par l'impact d'un astéroïde ou d'une comète en milieu océanique.
    """

    @classmethod
    def calculate_initial_wave_height(cls, impactor_diameter_m: float, water_depth_m: float = 4000.0) -> float:
        """
        Calcule la hauteur initiale de la vague d'impact océanique H0 en eau profonde.

        Equations:
            H_0 = 0.05 \\cdot d_i \\cdot \\left(\\frac{d_i}{d_w}\\right)^{0.5}
        """
        return 0.05 * impactor_diameter_m * math.sqrt(impactor_diameter_m / water_depth_m)

    @classmethod
    def calculate_tsunami_celerity(cls, water_depth_m: float) -> float:
        """
        Calcule la célérité de l'onde de tsunami en eau profonde : c = sqrt(g * d)

        Equations:
            c = \\sqrt{g \\cdot d}
        """
        return math.sqrt(GRAVITY_EARTH * water_depth_m)

    @classmethod
    def green_law_amplification(cls, initial_height_m: float, deep_depth_m: float, shallow_depth_m: float) -> float:
        """
        Calcule l'amplification de la vague sur la côte par la loi de Green.

        Equations:
            H_{\\text{coast}} = H_{\\text{initial}} \\cdot \\left(\\frac{d_{\\text{deep}}}{d_{\\text{shallow}}}\\right)^{1/4}
        """
        if shallow_depth_m <= 0:
            shallow_depth_m = 5.0
        return initial_height_m * ((deep_depth_m / shallow_depth_m) ** 0.25)

    @classmethod
    def simulate_ocean_impact_tsunami(
        cls, impactor_diameter_m: float, distance_from_impact_km: float
    ) -> dict[str, Any]:
        """Simule la propagation et le déferlement du tsunami d'impact."""
        h0 = cls.calculate_initial_wave_height(impactor_diameter_m)
        c_deep = cls.calculate_tsunami_celerity(4000.0)  # ~198 m/s = 712 km/h
        travel_time_hours = (distance_from_impact_km * 1000.0) / (c_deep * 3600.0)

        # Atténuation géométrique en eau profonde H(r) = H0 * (r0 / r)
        r0 = impactor_diameter_m * 5.0
        r_m = max(distance_from_impact_km * 1000.0, r0)
        h_deep_at_r = h0 * (r0 / r_m)

        # Runup côtoyer à 10m de profondeur
        h_coast = cls.green_law_amplification(h_deep_at_r, 4000.0, 10.0)

        return {
            "initial_deep_water_wave_height_m": h0,
            "tsunami_celerity_km_h": c_deep * 3.6,
            "travel_time_hours": travel_time_hours,
            "deep_water_height_at_target_m": h_deep_at_r,
            "coastal_runup_height_m": h_coast,
        }
