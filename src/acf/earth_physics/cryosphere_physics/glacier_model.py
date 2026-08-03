"""
Glacier Mass Balance & Accumulation/Ablation Model
"""


class GlacierMassBalance:
    """Modèle de bilan de masse des glaciers (Accumulation vs Ablation)."""

    @classmethod
    def net_mass_balance(cls, accumulation_m: float, ablation_m: float) -> float:
        return accumulation_m - ablation_m
