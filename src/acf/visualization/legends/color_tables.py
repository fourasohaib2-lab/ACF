"""
Atmospheric Complexity Framework (ACF)

Scientific Color Palettes & Legend Generation Module (WMO, Radar, Satellite, Temperature, Severe Weather)
"""

from typing import Any


class ColorTableRegistry:
    """
    Registre universel des palettes de couleurs scientifiques WMO, Radar, Satellite et Météo.
    """

    COLOR_MAPS: dict[str, list[tuple[float, str]]] = {
        # 1. Temperature Palette (°C)
        "temperature_wmo": [
            (-60.0, "#4A00E0"),
            (-40.0, "#0055FF"),
            (-20.0, "#00AAFF"),
            (0.0, "#00FFFF"),
            (10.0, "#00FF55"),
            (20.0, "#FFFF00"),
            (30.0, "#FF7700"),
            (45.0, "#FF0000"),
        ],
        # 2. NEXRAD Radar Reflectivity (dBZ)
        "radar_reflectivity": [
            (5.0, "#00ECEC"),
            (15.0, "#01A0F6"),
            (25.0, "#0000F6"),
            (35.0, "#00FF00"),
            (45.0, "#00C800"),
            (50.0, "#FFFF00"),
            (55.0, "#E7C000"),
            (60.0, "#FF0000"),
            (65.0, "#D60000"),
            (70.0, "#C00000"),
            (75.0, "#FF00FF"),
        ],
        # 3. Severe Storm CAPE (J/kg)
        "cape_severe": [
            (0.0, "#FFFFFF"),
            (250.0, "#C0E0FF"),
            (500.0, "#80B0FF"),
            (1000.0, "#00FF00"),
            (2000.0, "#FFFF00"),
            (3000.0, "#FF7700"),
            (4000.0, "#FF0000"),
            (6000.0, "#A000FF"),
        ],
        # 4. Satellite IR Cloud Top Temperature (K)
        "satellite_ir_ctt": [
            (180.0, "#FFFFFF"),
            (200.0, "#FF00FF"),
            (220.0, "#FF0000"),
            (240.0, "#FFFF00"),
            (260.0, "#00FF00"),
            (280.0, "#00FFFF"),
            (300.0, "#000080"),
        ],
        # 5. Wind Velocity (m/s / knots)
        "wind_speed": [
            (0.0, "#FFFFFF"),
            (5.0, "#99CCFF"),
            (10.0, "#0066FF"),
            (20.0, "#00CC00"),
            (30.0, "#FFFF00"),
            (40.0, "#FF6600"),
            (50.0, "#FF0000"),
            (75.0, "#CC00CC"),
        ],
    }

    @classmethod
    def get_palette(cls, name: str) -> list[tuple[float, str]]:
        """Récupère une table de couleurs par son nom."""
        return cls.COLOR_MAPS.get(name, cls.COLOR_MAPS["temperature_wmo"])

    @classmethod
    def generate_legend(cls, name: str, unit: str = "") -> dict[str, Any]:
        """Génère une structure de légende scientifique complète pour le panneau AWCI."""
        palette = cls.get_palette(name)
        return {
            "name": name,
            "unit": unit,
            "stops": [{"value": val, "color": color} for val, color in palette],
            "min_val": palette[0][0],
            "max_val": palette[-1][0],
        }
