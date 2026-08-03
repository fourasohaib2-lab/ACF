"""
Adaptive Timestep & CFL Condition Manager Module
"""


class AdaptiveTimestepManager:
    """Gestionnaire de pas de temps adaptatif et de condition de stabilité CFL (Courant-Friedrichs-Lewy)."""

    @classmethod
    def compute_cfl_timestep(cls, dx_m: float, max_velocity_m_s: float, cfl_target: float = 0.5) -> float:
        return (cfl_target * dx_m) / max(0.1, max_velocity_m_s)
