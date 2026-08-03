"""
Atmospheric Vorticity Module (zeta = dv/dx - du/dy)
"""


class VorticityCalculator:
    """Calculateur de la vorticité relative et absolue."""

    @classmethod
    def compute_relative_vorticity(cls, dv_dx: float, du_dy: float) -> float:
        return dv_dx - du_dy
