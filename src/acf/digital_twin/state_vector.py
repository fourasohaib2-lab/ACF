"""
Atmospheric Complexity Framework (ACF)

Global Earth State Vector Module (Phase 2)
(Atmosphere, Ocean, Hydrology, Climate, Cryosphere, Space Weather, Geology, Aviation, AI State Vector)
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class GlobalEarthStateVector:
    """
    Vecteur d'état unifié et multidomaine de la planète Terre.

    NOTE (correction — operationally dangerous): every field below used
    to default to a specific, plausible-looking fabricated value
    (temp_2m_c=15.2, cape_j_kg=1250.0, sst_c=18.5, co2_ppm=422.0,
    kp_index=4.5, max_recent_earthquake_mw=6.8,
    ai_model_active="GraphCast + NeuralGCM Ensemble",
    prediction_confidence_pct=92.5, etc.) - so constructing
    GlobalEarthStateVector() with zero arguments (as
    digital_twin.planet_state.GlobalEarthState's own field default
    factory does) silently produced a complete, internally-consistent-
    looking "current state of planet Earth" with 0 connection to any
    real observation. This is the same fabrication already found and
    fixed for GlobalEarthState.active_warnings_count/health_status in
    planet_state.py, but the state_vector it wraps - the actual bulk of
    the fabricated data - was missed by that fix. Fields now default to
    None; a caller with real values supplies them explicitly (as
    tests/test_digital_twin_platform.py's test already does), and
    to_dict() honestly reports whatever was actually supplied.
    """

    # 1. Atmosphere
    temp_2m_c: float | None = None
    pressure_hpa: float | None = None
    wind_speed_m_s: float | None = None
    precip_rate_mm_h: float | None = None
    cape_j_kg: float | None = None

    # 2. Ocean
    sst_c: float | None = None
    sss_psu: float | None = None
    significant_wave_height_m: float | None = None
    sea_level_anomaly_m: float | None = None

    # 3. Hydrology
    river_discharge_m3_s: float | None = None
    soil_moisture_cm3_cm3: float | None = None

    # 4. Climate
    oni_index: float | None = None
    nao_index: float | None = None
    co2_ppm: float | None = None

    # 5. Space Weather
    kp_index: float | None = None
    dst_nt: float | None = None
    tec_tecu: float | None = None
    solar_wind_speed_km_s: float | None = None

    # 6. Geology
    max_recent_earthquake_mw: float | None = None
    active_volcanoes_count: int | None = None

    # 7. AI & Predictions
    ai_model_active: str | None = None
    prediction_confidence_pct: float | None = None

    def to_dict(self) -> dict[str, Any]:
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
