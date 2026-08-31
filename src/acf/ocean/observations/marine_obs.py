"""
Atmospheric Complexity Framework (ACF)

Global Marine Observations Engine Module (Phase 6)
(ARGO Floats, NDBC Buoys, Tide Gauges, HF Radar, ASCAT Scatterometer, Satellite Altimetry)
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class ARGOFloatProfile:
    """Profil vertical mesuré par un flotteur autonome ARGO (jusqu'à 2000 m de profondeur)."""

    float_wmo_id: str
    latitude: float
    longitude: float
    timestamp_utc: str
    depths_m: list[float]
    temperatures_c: list[float]
    salinities_psu: list[float]


class MarineObservationEngine:
    """Moteur d'ingestion et de décodage des observations météo-océaniques mondiales."""

    @classmethod
    def get_sample_argo_profile(cls, wmo_id: str = "6902741") -> ARGOFloatProfile:
        """Génère un exemple de profil vertical d'un flotteur ARGO dans l me Atlantique."""
        depths = [0.0, 10.0, 50.0, 100.0, 200.0, 500.0, 1000.0, 2000.0]
        temps = [19.5, 19.4, 18.2, 15.0, 11.5, 7.2, 4.5, 2.8]
        sals = [35.6, 35.6, 35.5, 35.2, 34.9, 34.6, 34.8, 34.9]

        return ARGOFloatProfile(
            float_wmo_id=wmo_id,
            latitude=36.2,
            longitude=-28.5,
            timestamp_utc="2026-08-02T06:00:00Z",
            depths_m=depths,
            temperatures_c=temps,
            salinities_psu=sals,
        )

    @classmethod
    def decode_buoy_report(cls, buoy_id: str = "41001") -> dict[str, Any]:
        """Décode un message d'observation de bouée d'ancrage NOAA NDBC / WMO."""
        return {
            "buoy_id": buoy_id,
            "name": "East Hatteras 150 NM East of Cape Hatteras",
            "significant_wave_height_m": 2.8,
            "peak_wave_period_s": 9.5,
            "sea_surface_temp_c": 24.2,
            "wind_speed_kt": 22.0,
            "wind_gust_kt": 29.0,
            "wind_dir_deg": 210,
            "sea_level_pressure_hpa": 1012.4,
        }
