"""
Atmospheric Complexity Framework (ACF)

Global Earth State Vector Module (Phase 2)
(Atmosphere, Ocean, Hydrology, Climate, Cryosphere, Space Weather, Geology, Aviation, AI State Vector)
"""

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class GlobalEarthStateVector:
    """Vecteur d'état unifié et multidomaine de la planète Terre."""

    # 1. Atmosphere
    temp_2m_c: float = 15.2
    pressure_hpa: float = 1013.25
    wind_speed_m_s: float = 8.5
    precip_rate_mm_h: float = 1.2
    cape_j_kg: float = 1250.0

    # 2. Ocean
    sst_c: float = 18.5
    sss_psu: float = 35.2
    significant_wave_height_m: float = 2.4
    sea_level_anomaly_m: float = 0.05

    # 3. Hydrology
    river_discharge_m3_s: float = 340.0
    soil_moisture_cm3_cm3: float = 0.25

    # 4. Climate
    oni_index: float = 0.8
    nao_index: float = 1.2
    co2_ppm: float = 422.0

    # 5. Space Weather
    kp_index: float = 4.5
    dst_nt: float = -45.0
    tec_tecu: float = 35.0
    solar_wind_speed_km_s: float = 480.0

    # 6. Geology
    max_recent_earthquake_mw: float = 6.8
    active_volcanoes_count: int = 14

    # 7. AI & Predictions
    ai_model_active: str = "GraphCast + NeuralGCM Ensemble"
    prediction_confidence_pct: float = 92.5

    def to_dict(self) -> Dict[str, Any]:
        """Exporte le vecteur d'état complet sous forme de dictionnaire."""
        return {
            "atmosphere": {
                "temp_2m_c": self.temp_2m_c,
                "pressure_hpa": self.pressure_hpa,
                "wind_speed_m_s": self.wind_speed_m_s,
                "precip_rate_mm_h": self.precip_rate_mm_h,
                "cape_j_kg": self.cape_j_kg,
            },
            "ocean": {
                "sst_c": self.sst_c,
                "sss_psu": self.sss_psu,
                "significant_wave_height_m": self.significant_wave_height_m,
                "sea_level_anomaly_m": self.sea_level_anomaly_m,
            },
            "hydrology": {
                "river_discharge_m3_s": self.river_discharge_m3_s,
                "soil_moisture_cm3_cm3": self.soil_moisture_cm3_cm3,
            },
            "climate": {
                "oni_index": self.oni_index,
                "nao_index": self.nao_index,
                "co2_ppm": self.co2_ppm,
            },
            "space_weather": {
                "kp_index": self.kp_index,
                "dst_nt": self.dst_nt,
                "tec_tecu": self.tec_tecu,
                "solar_wind_speed_km_s": self.solar_wind_speed_km_s,
            },
            "geology": {
                "max_recent_earthquake_mw": self.max_recent_earthquake_mw,
                "active_volcanoes_count": self.active_volcanoes_count,
            },
            "ai": {
                "ai_model_active": self.ai_model_active,
                "prediction_confidence_pct": self.prediction_confidence_pct,
            },
        }
