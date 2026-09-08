"""
Atmospheric Complexity Framework (ACF)

Tectonic Plates & Continental Drift Module (Phase 2)
(African, Eurasian, Pacific, Nazca, North/South American Plates, Velocity, Azimuth, Boundaries)
"""

from dataclasses import dataclass


@dataclass
class Plate:
    """Description scientifique d'une plaque tectonique lithosphérique."""

    plate_id: str
    name: str
    velocity_cm_year: float
    azimuth_deg: float
    area_million_km2: float
    plate_type: str  # e.g., "Oceanic", "Continental", "Mixed"
    boundary_types: list[str]
    subduction_zones: list[str]


TECTONIC_PLATES_REGISTRY: dict[str, Plate] = {
    "pacific_plate": Plate(
        plate_id="pacific_plate",
        name="Pacific Plate",
        velocity_cm_year=8.5,
        azimuth_deg=305.0,
        area_million_km2=103.3,
        plate_type="Oceanic",
        boundary_types=["Subduction", "Transform", "Divergent"],
        subduction_zones=["Japan Trench", "Mariana Trench", "Aleutian Trench"],
    ),
    "eurasian_plate": Plate(
        plate_id="eurasian_plate",
        name="Eurasian Plate",
        velocity_cm_year=2.5,
        azimuth_deg=95.0,
        area_million_km2=67.8,
        plate_type="Continental",
        boundary_types=["Collision", "Transform"],
        subduction_zones=["Himalayan Collision Zone", "Hellenic Arc"],
    ),
    "african_plate": Plate(
        plate_id="african_plate",
        name="African Plate",
        velocity_cm_year=2.15,
        azimuth_deg=25.0,
        area_million_km2=61.3,
        plate_type="Mixed",
        boundary_types=["Rift", "Divergent", "Collision"],
        subduction_zones=["East African Rift System"],
    ),
    "nazca_plate": Plate(
        plate_id="nazca_plate",
        name="Nazca Plate",
        velocity_cm_year=7.2,
        azimuth_deg=80.0,
        area_million_km2=15.6,
        plate_type="Oceanic",
        boundary_types=["Subduction", "Divergent"],
        subduction_zones=["Peru-Chile Trench"],
    ),
}


class PlateDatabase:
    """
    Base de données et registre des grandes plaques tectoniques mondiales.

    NOTE (correction): docstring used to claim "14 grandes plaques" -
    only 4 are actually registered (Pacific, Eurasian, African, Nazca).
    """

    @classmethod
    def get_plate(cls, key: str) -> Plate | None:
        return TECTONIC_PLATES_REGISTRY.get(key.lower())

    @classmethod
    def list_plates(cls) -> list[str]:
        return list(TECTONIC_PLATES_REGISTRY.keys())
