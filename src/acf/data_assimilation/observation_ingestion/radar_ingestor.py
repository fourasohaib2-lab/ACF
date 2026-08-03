"""
Doppler Radar Mosaic & QPE Ingestion Module (Z = a * R^b)
"""



class RadarIngestor:
    """Gestionnaire d'ingestion des réflectivités radar Z et vitesses Doppler."""

    @classmethod
    def compute_qpe_rainfall_rate(cls, reflectivity_z_dbz: float, a: float = 200.0, b: float = 1.6) -> float:
        """Z = a * R^b -> R = (Z_linear / a)^(1/b) mm/h."""
        z_linear = 10.0 ** (reflectivity_z_dbz / 10.0)
        return (z_linear / a) ** (1.0 / b)
