"""
Atmospheric Complexity Framework (ACF)

Global Geological Faults Database Module (Phase 3)
(San Andreas, North Anatolian, Alpine Fault, Dead Sea Transform, Japan Trench, Slip Rate mm/yr)
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class FaultSegment:
    """Description d'une faille géologique active."""
    fault_id: str
    name: str
    fault_type: str  # e.g., "Strike-Slip", "Normal", "Reverse / Thrust", "Megathrust"
    length_km: float
    slip_rate_mm_year: float
    locking_depth_km: float
    max_credible_magnitude_mw: float
    historic_earthquakes: List[str]
    hazard_level: str


FAULT_REGISTRY: Dict[str, FaultSegment] = {
    "san_andreas": FaultSegment(
        fault_id="san_andreas",
        name="San Andreas Fault System",
        fault_type="Right-Lateral Strike-Slip",
        length_km=1200.0,
        slip_rate_mm_year=35.0,
        locking_depth_km=15.0,
        max_credible_magnitude_mw=8.1,
        historic_earthquakes=["1906 San Francisco (Mw 7.9)", "1857 Fort Tejon (Mw 7.9)"],
        hazard_level="CRITICAL / HIGH SEISMIC HAZARD",
    ),
    "north_anatolian": FaultSegment(
        fault_id="north_anatolian",
        name="North Anatolian Fault Zone",
        fault_type="Right-Lateral Strike-Slip",
        length_km=1500.0,
        slip_rate_mm_year=24.0,
        locking_depth_km=12.0,
        max_credible_magnitude_mw=7.8,
        historic_earthquakes=["1999 Izmit (Mw 7.6)", "1939 Erzincan (Mw 7.8)"],
        hazard_level="CRITICAL / HIGH SEISMIC HAZARD",
    ),
    "japan_trench_megathrust": FaultSegment(
        fault_id="japan_trench_megathrust",
        name="Japan Trench Megathrust",
        fault_type="Subduction Megathrust",
        length_km=800.0,
        slip_rate_mm_year=80.0,
        locking_depth_km=50.0,
        max_credible_magnitude_mw=9.2,
        historic_earthquakes=["2011 Tohoku-Oki (Mw 9.1)", "869 Jogan (Mw 8.6)"],
        hazard_level="EXTREME / TSUNAMIGENIC MEGATHRUST",
    ),
}


class FaultDatabase:
    """Base de données et registre des grandes failles sismogènes mondiales."""

    @classmethod
    def get_fault(cls, key: str) -> Optional[FaultSegment]:
        return FAULT_REGISTRY.get(key.lower())

    @classmethod
    def list_faults(cls) -> List[str]:
        return list(FAULT_REGISTRY.keys())
