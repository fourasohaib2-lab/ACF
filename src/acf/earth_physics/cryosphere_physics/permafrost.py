"""
Permafrost Thaw & Carbon/Methane Release Model
"""


class PermafrostThawModel:
    """Modèle de dégel du permafrost et de libération de méthane et $CO_2$."""

    @classmethod
    def compute_ch4_emission_megatons(cls, thaw_depth_increase_m: float) -> float:
        return thaw_depth_increase_m * 14.5
