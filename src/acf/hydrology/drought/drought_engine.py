"""
Atmospheric Complexity Framework (ACF)

Hydrological & Agricultural Drought Monitoring Engine Module (Phase 7)
(SPI, SPEI, Soil Moisture Drought Index SMDI, Streamflow Drought Index SDI)
"""

from typing import Any, Dict, List


class HydrologicalDroughtEngine:
    """
    Moteur de détection et de classification des sécheresses météorologiques, agricoles et hydrologiques.
    """

    @staticmethod
    def classify_spi_drought(spi_value: float) -> Dict[str, str]:
        """Classifie le niveau de sécheresse selon l'indice SPI (OMM Standard)."""
        if spi_value >= 2.0:
            cat = "Extremely Wet"
        elif spi_value >= 1.5:
            cat = "Severely Wet"
        elif spi_value >= 1.0:
            cat = "Moderately Wet"
        elif spi_value > -1.0:
            cat = "Near Normal"
        elif spi_value > -1.5:
            cat = "Moderate Drought"
        elif spi_value > -2.0:
            cat = "Severe Drought"
        else:
            cat = "Extreme Drought"

        return {"spi_value": str(round(spi_value, 2)), "drought_category": cat}

    @classmethod
    def evaluate_basin_drought_status(cls, monthly_streamflow_m3_s: List[float], mean_streamflow_m3_s: float) -> Dict[str, Any]:
        """Évalue l'indice de sécheresse des cours d'eau (Streamflow Drought Index SDI)."""
        if not monthly_streamflow_m3_s or mean_streamflow_m3_s <= 0:
            return {"sdi": 0.0, "status": "Normal"}

        current_q = monthly_streamflow_m3_s[-1]
        ratio = current_q / mean_streamflow_m3_s

        if ratio < 0.3:
            status = "Hydrological Drought Emergency (Débit très faible)"
        elif ratio < 0.6:
            status = "Hydrological Drought Warning"
        else:
            status = "Normal Streamflow"

        return {
            "current_discharge_m3_s": current_q,
            "mean_discharge_m3_s": mean_streamflow_m3_s,
            "discharge_ratio": round(ratio, 2),
            "status": status,
        }
