"""
Radiative Energy Balance Solver Module
"""


class RadiativeBalanceSolver:
    """Résolveur de bilan radiatif net (Shortwave In minus Longwave Out)."""

    @classmethod
    def net_radiative_forcing(cls, shortwave_in: float, albedo: float, longwave_out: float) -> float:
        absorbed_shortwave = shortwave_in * (1.0 - albedo)
        return absorbed_shortwave - longwave_out
