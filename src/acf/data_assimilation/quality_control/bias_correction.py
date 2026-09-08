"""
Variational Bias Correction (VarBC) Module
"""


class VariationalBiasCorrection:
    """Correction variationnelle de biais d'observation (VarBC)."""

    @classmethod
    def correct_bias(cls, raw_obs: float, estimated_bias: float) -> float:
        return raw_obs - estimated_bias
