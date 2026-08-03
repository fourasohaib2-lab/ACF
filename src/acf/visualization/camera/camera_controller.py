"""
Atmospheric Complexity Framework (ACF)

Camera Controller Module (2D/3D Perspective, Orbit & Flight Navigation)
"""

from typing import Any, Dict


class CameraController:
    """
    Contrôleur de caméra scientifique 2D/3D avec support des projections, survol et signets.
    """

    def __init__(self, mode: str = "Perspective"):
        self.mode = mode  # "Perspective", "Orthographic", "Orbit", "Flight"
        self.lat = 48.8566
        self.lon = 2.3522
        self.altitude_km = 500.0
        self.heading_deg = 0.0
        self.pitch_deg = -90.0  # -90° = vue du dessus
        self.roll_deg = 0.0
        self.fov_deg = 60.0
        self.bookmarks: Dict[str, Dict[str, float]] = {
            "Global": {"lat": 0.0, "lon": 0.0, "altitude_km": 12000.0, "pitch_deg": -90.0},
            "Europe": {"lat": 48.0, "lon": 10.0, "altitude_km": 2500.0, "pitch_deg": -90.0},
            "North_America": {"lat": 40.0, "lon": -100.0, "altitude_km": 4000.0, "pitch_deg": -90.0},
            "Storm_3D_View": {"lat": 45.0, "lon": 5.0, "altitude_km": 50.0, "pitch_deg": -45.0},
        }

    def set_position(self, lat: float, lon: float, altitude_km: float):
        """Définit la position géographique de la caméra."""
        self.lat = max(-90.0, min(90.0, lat))
        self.lon = (lon + 180.0) % 360.0 - 180.0
        self.altitude_km = max(0.1, altitude_km)

    def pan(self, delta_lat: float, delta_lon: float):
        """Déplace la caméra sur la sphère terrestre."""
        self.set_position(self.lat + delta_lat, self.lon + delta_lon, self.altitude_km)

    def zoom(self, factor: float):
        """Zoom (factor < 1.0 zoom avant, factor > 1.0 zoom arrière)."""
        self.altitude_km = max(0.5, self.altitude_km * factor)

    def rotate_and_tilt(self, delta_heading: float, delta_pitch: float):
        """Fait pivoter et incliner la caméra."""
        self.heading_deg = (self.heading_deg + delta_heading) % 360.0
        self.pitch_deg = max(-90.0, min(0.0, self.pitch_deg + delta_pitch))

    def goto_bookmark(self, name: str) -> bool:
        """Oriente instantanément la caméra sur un signet géographique."""
        if name in self.bookmarks:
            b = self.bookmarks[name]
            self.set_position(b["lat"], b["lon"], b["altitude_km"])
            if "pitch_deg" in b:
                self.pitch_deg = b["pitch_deg"]
            return True
        return False

    def get_state(self) -> Dict[str, Any]:
        """Retourne l'état complet du système de caméra."""
        return {
            "mode": self.mode,
            "position": {"lat": self.lat, "lon": self.lon, "altitude_km": self.altitude_km},
            "orientation": {"heading": self.heading_deg, "pitch": self.pitch_deg, "roll": self.roll_deg},
            "fov": self.fov_deg,
        }
