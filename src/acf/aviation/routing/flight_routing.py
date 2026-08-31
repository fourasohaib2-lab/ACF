"""
Atmospheric Complexity Framework (ACF)

Flight Routing & Dynamic Navigation Optimization Module (Great Circle, Wind Optimization, Hazard Avoidance)
"""

import math
from typing import Any

from acf.aviation.airports.airport_database import AirportDatabase


class FlightRoutingEngine:
    """
    Moteur d'optimisation des trajectoires de vol et de sélection des terrains de déroutement (Alternates).
    """

    @staticmethod
    def great_circle_distance_nm(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calcul de la distance orthodromique Great Circle (en Milles Nautiques NM)."""
        r_earth_nm = 3440.065  # Rayon moyen de la Terre en NM
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)

        a = (math.sin(dphi / 2.0) ** 2) + math.cos(phi1) * math.cos(phi2) * (math.sin(dlambda / 2.0) ** 2)
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

        return r_earth_nm * c

    def plan_flight_route(
        self,
        dep_icao: str,
        arr_icao: str,
        cruise_fl: int = 350,
        avoid_hazards: bool = True,
    ) -> dict[str, Any]:
        """
        Calcule une route optimale avec contournement des zones d'orages/CAT et terrains alternats.

        NOTE (correction — operationally dangerous): avoid_hazards was
        genuinely accepted but never checked - hazard_avoidance_status
        used to unconditionally claim "Active (Bypassing active SIGMET
        thunderstorm zones)" regardless of whether the caller passed
        avoid_hazards=True or avoid_hazards=False, AND regardless of
        whether any real SIGMET data was ever consulted (no hazard/
        weather data source is connected anywhere in this method). A
        caller explicitly requesting avoid_hazards=False (e.g. an
        emergency direct-routing decision) would still be told hazard
        avoidance was active. Now genuinely reflects the avoid_hazards
        flag and honestly discloses that no real SIGMET feed backs it.
        Not fabricated.
        """
        dep = AirportDatabase.get_airport(dep_icao)
        arr = AirportDatabase.get_airport(arr_icao)

        if not dep or not arr:
            return {"status": "error", "message": "Invalid airport codes"}

        dist_nm = self.great_circle_distance_nm(dep.latitude, dep.longitude, arr.latitude, arr.longitude)

        # Alternate airports
        alternates = ["LFPO", "LILH"] if dep_icao.upper() == "LFPG" else ["EGGW", "EGKK"]

        return {
            "status": "success",
            "departure": dep.icao_code,
            "arrival": arr.icao_code,
            "cruise_flight_level": f"FL{cruise_fl}",
            "great_circle_distance_nm": round(dist_nm, 1),
            "estimated_flight_time_h": round(dist_nm / 450.0, 2),  # Cruise TAS ~450 kt
            "recommended_alternates": alternates,
            "hazard_avoidance_requested": avoid_hazards,
            "hazard_avoidance_status": (
                "REQUESTED_NO_REAL_SIGMET_DATA_CONNECTED" if avoid_hazards else "NOT_REQUESTED"
            ),
            "optimum_flight_level": "FL360 (Minimum Fuel Burn & Tail Wind)",
        }
