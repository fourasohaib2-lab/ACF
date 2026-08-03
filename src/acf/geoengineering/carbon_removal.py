"""
Atmospheric Complexity Framework (ACF)

Carbon Dioxide Removal (CDR) Engine Module (Phase 3)
(CarbonRemovalEngine modeling DAC, BECCS, Enhanced Weathering, Biochar, Afforestation, Ocean Alkalinity)
"""

from dataclasses import dataclass


@dataclass
class CDRTechniqueResult:
    """Description et métriques d'une méthode de captage et d'élimination du CO2 (CDR)."""
    technique_name: str
    annual_removal_capacity_gt_co2: float
    durability_years: float  # Durée de stockage (10 à 10000+ ans)
    cost_usd_per_ton_co2: float
    energy_consumption_mwh_per_ton: float
    land_area_required_km2_per_gt: float
    readiness_level_trl: int  # Technology Readiness Level (1 à 9)


class CarbonRemovalEngine:
    """
    Moteur de modélisation et d'évaluation des techniques d'élimination du CO2 (CDR).
    """

    @classmethod
    def evaluate_direct_air_capture(cls, capacity_gt_co2: float = 1.0) -> CDRTechniqueResult:
        """Simule le captage direct du CO2 dans l'air (DAC + Mineralization)."""
        return CDRTechniqueResult(
            technique_name="Direct Air Capture with Carbon Storage (DACCS)",
            annual_removal_capacity_gt_co2=capacity_gt_co2,
            durability_years=10000.0,  # Minéralisation basaltique permanente
            cost_usd_per_ton_co2=250.0,
            energy_consumption_mwh_per_ton=2.1,
            land_area_required_km2_per_gt=50.0,
            readiness_level_trl=7,
        )

    @classmethod
    def evaluate_enhanced_weathering(cls, rock_dust_gt: float = 5.0) -> CDRTechniqueResult:
        """Simule l'altération forcée des roches silicatées (Basalte / Olivine)."""
        removal = rock_dust_gt * 0.3  # ~0.3 t CO2 capturé par tonne de basalte
        return CDRTechniqueResult(
            technique_name="Enhanced Rock Weathering (ERW)",
            annual_removal_capacity_gt_co2=removal,
            durability_years=100000.0,  # Stockage sous forme de bicarbionates dissous
            cost_usd_per_ton_co2=120.0,
            energy_consumption_mwh_per_ton=0.2,
            land_area_required_km2_per_gt=500000.0,
            readiness_level_trl=6,
        )
