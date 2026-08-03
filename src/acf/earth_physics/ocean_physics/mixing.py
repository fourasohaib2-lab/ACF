"""
Ocean Vertical & Mixed Layer Mixing Module
"""


class OceanVerticalMixing:
    """Modèle de mélange de la couche limite océanique (Turbulent Kinetic Energy TKE)."""

    @classmethod
    def mixed_layer_depth_m(cls, wind_stress: float, heat_flux: float) -> float:
        return 45.0
