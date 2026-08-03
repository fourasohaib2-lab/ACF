"""
Atmospheric Complexity Framework (ACF)

Volcanology & Active Volcanoes Registry Module (Phase 7)
(Volcano, VEI Scale 0-8, Magma Composition, Plinian Eruptions, SO2 Gas)
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class Volcano:
    """Description d'un édifice volcanique actif."""
    volcano_id: str
    name: str
    country: str
    elevation_m: float
    latitude: float
    longitude: float
    volcano_type: str  # e.g., "Stratovolcano", "Shield Volcano", "Caldera"
    magma_composition: str  # e.g., "Basaltic", "Andesitic", "Dacitic", "Rhyolitic"
    last_known_eruption_year: int
    vei_max: int  # Volcanic Explosivity Index (0 to 8)
    hazards: List[str]


VOLCANO_REGISTRY: Dict[str, Volcano] = {
    "vesuvius": Volcano(
        volcano_id="vesuvius",
        name="Mount Vesuvius",
        country="Italy",
        elevation_m=1281.0,
        latitude=40.821,
        longitude=14.426,
        volcano_type="Complex Stratovolcano",
        magma_composition="Tephri-phonolite / Dacitic",
        last_known_eruption_year=1944,
        vei_max=5,
        hazards=["Pyroclastic Flows", "Tephra Fall", "Lahars"],
    ),
    "kilauea": Volcano(
        volcano_id="kilauea",
        name="Kilauea",
        country="USA (Hawaii)",
        elevation_m=1247.0,
        latitude=19.421,
        longitude=-155.287,
        volcano_type="Shield Volcano",
        magma_composition="Tholeiitic Basalt",
        last_known_eruption_year=2024,
        vei_max=1,
        hazards=["Lava Flows", "Vog Gas (SO2)", "Pele's Hair"],
    ),
    "krakatoa": Volcano(
        volcano_id="krakatoa",
        name="Anak Krakatau",
        country="Indonesia",
        elevation_m=155.0,
        latitude=-6.102,
        longitude=105.423,
        volcano_type="Caldera / Volcanic Island",
        magma_composition="Andesitic",
        last_known_eruption_year=2023,
        vei_max=6,
        hazards=["Volcanic Tsunami", "Pyroclastic Flows", "Ash Plume"],
    ),
}


class VolcanoDatabase:
    """Base de données et registre des principaux volcans actifs de la Terre."""

    @classmethod
    def get_volcano(cls, key: str) -> Optional[Volcano]:
        return VOLCANO_REGISTRY.get(key.lower())

    @classmethod
    def list_volcanoes(cls) -> List[str]:
        return list(VOLCANO_REGISTRY.keys())
