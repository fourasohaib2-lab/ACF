"""
Atmospheric Complexity Framework (ACF)

Precipitation-Runoff Models & River Routing Module (Phase 2)
(SCS Curve Number Method, Green-Ampt Infiltration, Muskingum River Routing)
"""

from typing import Dict


class RunoffEngine:
    """
    Moteur d'infiltration du sol et de routage des crues en rivière.
    """

    @staticmethod
    def scs_curve_number_runoff(precipitation_mm: float, curve_number: float) -> Dict[str, float]:
        """
        Calcul du ruissellement direct Q par la méthode du Curve Number (SCS / USDA NRCS).
        S = (25400 / CN) - 254 (rétention potentielle maximale en mm).
        Ia = 0.2 * S (abstraction initiale).
        """
        if curve_number <= 0 or curve_number > 100:
            return {"runoff_mm": 0.0, "retention_s_mm": 0.0}

        s = (25400.0 / curve_number) - 254.0
        ia = 0.2 * s

        if precipitation_mm <= ia:
            return {"runoff_mm": 0.0, "retention_s_mm": s, "initial_abstraction_mm": ia}

        runoff_mm = ((precipitation_mm - ia) ** 2) / (precipitation_mm - ia + s)
        return {
            "runoff_mm": round(runoff_mm, 2),
            "retention_s_mm": round(s, 2),
            "initial_abstraction_mm": round(ia, 2),
        }

    @staticmethod
    def muskingum_routing(inflow_i0: float, inflow_i1: float, outflow_q0: float, k_hours: float, x_factor: float, dt_hours: float) -> float:
        """
        Calcul du routage de crue en rivière par la méthode de Muskingum.
        C0 = (-K*X + 0.5*dt) / D
        C1 = (K*X + 0.5*dt) / D
        C2 = (K*(1-X) - 0.5*dt) / D
        """
        d = k_hours * (1.0 - x_factor) + 0.5 * dt_hours
        if d <= 0:
            return inflow_i1

        c0 = (-k_hours * x_factor + 0.5 * dt_hours) / d
        c1 = (k_hours * x_factor + 0.5 * dt_hours) / d
        c2 = (k_hours * (1.0 - x_factor) - 0.5 * dt_hours) / d

        q1 = c0 * inflow_i1 + c1 * inflow_i0 + c2 * outflow_q0
        return max(0.0, q1)
