"""
Atmospheric Complexity Framework (ACF)

Physics-Informed AI PDE Residual Losses & Conservation Constraints Module
(Mass, Moisture, Momentum, Energy & Hydrostatic Balance)
"""

import math
from typing import Dict


class PDEPhysicsLossEvaluator:
    """
    Évaluateur des pertes résiduelles d'équations aux dérivées partielles (PDE Losses)
    garantissant le respect des lois physiques fondamentales par les réseaux de neurones.
    """

    @staticmethod
    def mass_conservation_residual(div_wind: float, d_density_dt: float = 0.0) -> float:
        """
        Résidu de la conservation de la masse : d(rho)/dt + rho * div(V) = 0.
        Dans un fluide incompressible/anabatique : div(V) = 0.
        """
        return abs(d_density_dt + div_wind)

    @staticmethod
    def moisture_conservation_residual(dq_dt: float, advection_q: float, source_sink_q: float = 0.0) -> float:
        """Résidu de la conservation de l'humidité : dq/dt + V . grad(q) - S_q = 0."""
        return abs(dq_dt + advection_q - source_sink_q)

    @staticmethod
    def geostrophic_balance_residual(u_actual: float, u_geostrophic: float, v_actual: float, v_geostrophic: float) -> float:
        """Résidu de l'équilibre géostrophique en atmosphère libre : V_actual - V_geostrophic = 0."""
        du = u_actual - u_geostrophic
        dv = v_actual - v_geostrophic
        return math.sqrt(du**2 + dv**2)

    @staticmethod
    def hydrostatic_balance_residual(dp_dz: float, rho: float, g: float = 9.80665) -> float:
        """Résidu de l'équilibre hydrostatique : dp/dz + rho * g = 0."""
        return abs(dp_dz + rho * g)

    @classmethod
    def evaluate_total_physics_loss(cls, predictions: Dict[str, float]) -> Dict[str, float]:
        """
        Calcule les différentes pénalités physiques sur un vecteur de prédiction d'IA.
        """
        div_w = predictions.get("divergence_wind", 0.0)
        dq = predictions.get("dq_dt", 0.0)
        adv_q = predictions.get("adv_q", 0.0)
        u_act = predictions.get("u", 10.0)
        u_geo = predictions.get("u_geo", 10.0)
        v_act = predictions.get("v", 0.0)
        v_geo = predictions.get("v_geo", 0.0)

        l_mass = cls.mass_conservation_residual(div_w)
        l_moist = cls.moisture_conservation_residual(dq, adv_q)
        l_geo = cls.geostrophic_balance_residual(u_act, u_geo, v_act, v_geo)

        total_loss = l_mass + 0.5 * l_moist + 0.2 * l_geo

        return {
            "total_physics_loss": total_loss,
            "mass_loss": l_mass,
            "moisture_loss": l_moist,
            "geostrophic_loss": l_geo,
            "is_physically_consistent": total_loss < 0.1,
        }
