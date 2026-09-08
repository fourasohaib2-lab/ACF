"""
Ocean-Sea Ice Thermal & Mechanical Coupling Module
"""


class OceanSeaIceCoupling:
    """Couplage thermique et dynamique entre l'océan et la banquise."""

    @classmethod
    def compute_heat_flux_to_ice(cls, ocean_temp_c: float, freezing_temp_c: float = -1.8) -> float:
        return max(0.0, (ocean_temp_c - freezing_temp_c) * 12.0)
