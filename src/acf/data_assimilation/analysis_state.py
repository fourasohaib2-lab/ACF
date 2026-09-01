"""
Earth Analysis State Vector Module (Phase 9)
(EarthAnalysisStateVector X = [T, P, U, V, q, O3, CO2, SST, Ice, Soil])
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class EarthAnalysisStateVector:
    """
    Vecteur d'analyse d'état global ré-assimilé X du système Terre.

    NOTE (correction): analysis_timestamp/quality_score used to default
    to a fixed "2026-08-02 12:00 UTC" / "98.6" respectively, and
    get_analysis_summary() unconditionally claimed
    "ANALYSIS_STATE_PRODUCED" for a bare EarthAnalysisStateVector() -
    but no DA engine in this package can actually produce a real
    analysis yet: EnsembleKalmanFilter.run_ensemble_update(),
    FourDVarEngine.minimize_4dvar() and
    HybridEnsembleVarDA.run_hybrid_assimilation() (this same package)
    all raise NotImplementedError for exactly this reason. This class
    is the natural downstream "result" object of those engines and had
    the identical issue. state_variables (the 10 physical variable
    names X = [T, P, U, V, q, O3, CO2, SST, Ice, Soil]) is genuine
    static structural metadata, unaffected.
    """

    analysis_timestamp: str | None = None
    state_variables: list[str] = field(
        default_factory=lambda: [
            "Temperature T",
            "Pressure P",
            "Wind U",
            "Wind V",
            "Specific Humidity q",
            "Ozone O3",
            "Carbon Dioxide CO2",
            "Sea Surface Temp SST",
            "Sea Ice",
            "Soil Moisture",
        ]
    )
    quality_score: float | None = None

    def get_analysis_summary(self) -> dict[str, Any]:
        produced = self.quality_score is not None and self.analysis_timestamp is not None
        return {
            "timestamp": self.analysis_timestamp,
            "variables_count": len(self.state_variables),
            "state_variables": self.state_variables,
            "analysis_quality_score": self.quality_score,
            "status": "ANALYSIS_STATE_PRODUCED" if produced else "NOT_PRODUCED_NO_REAL_ASSIMILATION_CONNECTED",
            "is_real_data": produced,
        }
