"""
Atmospheric Complexity Framework (ACF)

Planetary Boundaries Monitoring Engine Module (Phase 1)
(PlanetaryBoundaryEngine, PlanetaryBoundary, BoundaryAssessment tracking Rockström & Steffen 9 Planetary Boundaries)
"""

from dataclasses import dataclass


@dataclass
class PlanetaryBoundary:
    """Description d'une des 9 limites planétaires (Stockholm Resilience Centre)."""

    boundary_name: str
    control_variable: str
    pre_industrial_value: float
    safe_boundary_value: float
    current_value: float
    unit: str
    is_transgressed: bool
    risk_level: str  # SAFE, INCREASING_RISK, HIGH_RISK


@dataclass
class BoundaryAssessment:
    """Bilan global des 9 limites planétaires."""

    total_boundaries_count: int
    transgressed_count: int
    overall_safety_index_pct: float
    boundaries_status: dict[str, PlanetaryBoundary]


BOUNDARIES_REGISTRY: dict[str, PlanetaryBoundary] = {
    "climate_change": PlanetaryBoundary(
        boundary_name="Climate Change",
        control_variable="Atmospheric CO2 Concentration",
        pre_industrial_value=280.0,
        safe_boundary_value=350.0,
        current_value=425.0,
        unit="ppm",
        is_transgressed=True,
        risk_level="HIGH_RISK",
    ),
    "biosphere_integrity": PlanetaryBoundary(
        boundary_name="Biosphere Integrity",
        control_variable="Extinction Rate (E/MSY)",
        pre_industrial_value=1.0,
        safe_boundary_value=10.0,
        current_value=100.0,
        unit="E/MSY",
        is_transgressed=True,
        risk_level="HIGH_RISK",
    ),
    "land_system_change": PlanetaryBoundary(
        boundary_name="Land System Change",
        control_variable="Original Forest Area Remaining",
        pre_industrial_value=100.0,
        safe_boundary_value=75.0,
        current_value=60.0,
        unit="%",
        is_transgressed=True,
        risk_level="INCREASING_RISK",
    ),
    "freshwater_change": PlanetaryBoundary(
        boundary_name="Freshwater Change",
        control_variable="Global Streamflow Disruption & Soil Moisture",
        pre_industrial_value=0.0,
        safe_boundary_value=10.0,
        current_value=18.0,
        unit="%",
        is_transgressed=True,
        risk_level="INCREASING_RISK",
    ),
    "biogeochemical_flows": PlanetaryBoundary(
        boundary_name="Biogeochemical Flows (Nitrogen)",
        control_variable="Industrial N2 Fixation Rate",
        pre_industrial_value=0.0,
        safe_boundary_value=62.0,
        current_value=150.0,
        unit="Tg N / year",
        is_transgressed=True,
        risk_level="HIGH_RISK",
    ),
    "ocean_acidification": PlanetaryBoundary(
        boundary_name="Ocean Acidification",
        control_variable="Aragonite Saturation State (Omega)",
        pre_industrial_value=3.44,
        safe_boundary_value=2.75,
        current_value=2.80,
        unit="Omega ratio",
        is_transgressed=False,
        risk_level="INCREASING_RISK",
    ),
    "atmospheric_aerosols": PlanetaryBoundary(
        boundary_name="Atmospheric Aerosol Loading",
        control_variable="Regional Aerosol Optical Depth (AOD)",
        pre_industrial_value=0.05,
        safe_boundary_value=0.25,
        current_value=0.15,
        unit="AOD",
        is_transgressed=False,
        risk_level="SAFE",
    ),
    "novel_entities": PlanetaryBoundary(
        boundary_name="Novel Entities (Chemicals/Plastics)",
        control_variable="Release Rate of Synthetic Toxins and Plastics",
        pre_industrial_value=0.0,
        safe_boundary_value=10.0,
        current_value=85.0,
        unit="Arbitrary Index",
        is_transgressed=True,
        risk_level="HIGH_RISK",
    ),
    "stratospheric_ozone": PlanetaryBoundary(
        boundary_name="Stratospheric Ozone Depletion",
        control_variable="Ozone Column Concentration",
        pre_industrial_value=290.0,
        safe_boundary_value=275.0,
        current_value=285.0,
        unit="Dobson Units (DU)",
        is_transgressed=False,
        risk_level="SAFE",
    ),
}


class PlanetaryBoundaryEngine:
    """
    Moteur de suivi et d'évaluation des 9 limites planétaires (Stockholm Resilience Centre).
    """

    @classmethod
    def get_boundary(cls, key: str) -> PlanetaryBoundary | None:
        return BOUNDARIES_REGISTRY.get(key.lower())

    @classmethod
    def evaluate_planetary_boundaries(cls) -> BoundaryAssessment:
        """Génère un bilan global de transgression des limites planétaires."""
        total = len(BOUNDARIES_REGISTRY)
        transgressed = sum(1 for b in BOUNDARIES_REGISTRY.values() if b.is_transgressed)
        safety_index = ((total - transgressed) / total) * 100.0

        return BoundaryAssessment(
            total_boundaries_count=total,
            transgressed_count=transgressed,
            overall_safety_index_pct=safety_index,
            boundaries_status=dict(BOUNDARIES_REGISTRY),
        )
