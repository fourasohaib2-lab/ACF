"""
Atmospheric Complexity Framework (ACF)

Hydrological Observation & Remote Sensing Engine Module (Phase 8)
(River Gauges, Discharge Stations, SMAP Soil Moisture, GRACE Water Storage)
"""

from typing import Any


class HydrologicalObservationEngine:
    """
    Moteur d'ingestion et de décodage des observations de jaugeage de rivière, réservoirs et télédétection hydrologique.
    """

    @classmethod
    def get_river_gauge_reading(cls, station_id: str = "H5201010") -> dict[str, Any]:
        """
        Retourne la mesure d'une station de jaugeage de rivière (ex: Vigicrues Seine à Paris Austerlitz).

        NOTE (correction — Physics Guard): no real Vigicrues/gauge
        network feed is connected here - station_name/river_name/
        water_level_m/discharge_m3_s/timestamp_utc/vigicrues_alert_level
        are ALL fixed illustrative values for the one documented example
        station (Paris Austerlitz on the Seine), returned identically
        regardless of the actual `station_id` requested, with a fixed
        timestamp presented with no indication it isn't live. The
        existing test even asserted directly on these fabricated
        numbers, locking them in as if verified - the same test-gaming
        pattern found and fixed repeatedly elsewhere this session (e.g.
        science/observations/wmo_code_tables.py's METAR decoder,
        earth_physics/carbon_cycle/carbon_flux.py's carbon budget - the
        latter's own "is_real_data: False" marker is the established
        fix pattern applied here too). Marked explicitly as not live
        data instead of silently presented as if it were.
        """
        return {
            "station_id": station_id,
            "station_name": "PARIS (Austerlitz)",
            "river_name": "Seine",
            "water_level_m": 2.15,
            "discharge_m3_s": 340.0,
            "timestamp_utc": "2026-08-02T08:00:00Z",
            "vigicrues_alert_level": "GREEN",
            "is_real_data": False,
        }

    @classmethod
    def get_satellite_smap_moisture(cls, latitude: float, longitude: float) -> dict[str, Any]:
        """
        Extrait la mesure de l'humidité du sol issue du satellite NASA SMAP (0-5 cm).

        NOTE (correction — Physics Guard): no real SMAP data feed is
        connected - volumetric_soil_moisture_cm3_cm3 is a fixed
        illustrative value returned identically regardless of the
        actual latitude/longitude requested (the same fake-live-data
        pattern documented in get_river_gauge_reading() above). Marked
        explicitly as not live data.
        """
        return {
            "satellite": "NASA SMAP (Radiomètre L-band)",
            "latitude": latitude,
            "longitude": longitude,
            "volumetric_soil_moisture_cm3_cm3": 0.24,
            "quality_flag": "GOOD",
            "is_real_data": False,
        }
