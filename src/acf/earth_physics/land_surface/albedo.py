"""
Surface Albedo Parametrization Model
"""


class SurfaceAlbedoModel:
    """Paramétrisation de l'albédo de surface (Neige, Forêt, Océan, Désert)."""

    @classmethod
    def compute_effective_albedo(cls, surface_type: str = "Forest", snow_cover_pct: float = 0.0) -> float:
        base_albedo = 0.15 if surface_type == "Forest" else 0.06 if surface_type == "Ocean" else 0.30
        snow_albedo = 0.80
        return base_albedo * (1.0 - snow_cover_pct / 100.0) + snow_albedo * (snow_cover_pct / 100.0)
