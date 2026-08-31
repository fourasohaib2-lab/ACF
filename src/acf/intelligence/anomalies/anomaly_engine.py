"""
Atmospheric Complexity Framework (ACF)

Earth Anomaly Detection Engine Module (Phase 5)
(EarthAnomalyEngine detecting extreme weather, heatwaves, severe storms, earthquakes, solar flares)
"""

from dataclasses import dataclass


@dataclass
class DetectedEarthAnomaly:
    """Description d'une anomalie détectée sur la Terre."""

    anomaly_id: str
    domain: str
    anomaly_type: str
    severity_level: str
    confidence_pct: float
    physical_origin: str


class EarthAnomalyEngine:
    """
    Moteur de détection autonome des anomalies globales multi-domaines.
    """

    @classmethod
    def scan_for_anomalies(cls) -> list[DetectedEarthAnomaly]:
        """
        Scanne le vecteur d'état planétaire et identifie les anomalies en cours.

        NOTE (correction — operationally dangerous): this used to
        unconditionally return the same 2 fixed fabricated anomalies
        for ANY call, with 0 parameters and no real planetary state
        vector ever scanned - a fake "+4.2 sigma heatwave" at "98%
        confidence" and a fake "X2.4 solar flare" at "99.5%
        confidence". A caller trusting this "autonomous anomaly
        detection" could believe two genuine severe events were
        actively occurring when nothing was ever scanned. Not
        fabricated - now returns an empty list rather than fabricated
        detections.
        """
        return []
