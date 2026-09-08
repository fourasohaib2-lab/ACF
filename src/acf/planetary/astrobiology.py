"""
Atmospheric Complexity Framework (ACF)

Astrobiology & Planetary Habitability Engine Module (Phase 8)
(HabitabilityEngine calculating Habitability Index, Liquid Water Index, Biosignatures O2, O3, CH4, CO2, H2O)
"""

from dataclasses import dataclass

from acf.planetary.exoplanets import ExoplanetDatabase


@dataclass
class HabitabilityAssessment:
    """Bilan d'habitabilité et détection de biosignatures."""

    target_name: str
    habitability_index_pct: float
    potential_water: str
    detected_biosignatures: list[str]
    is_habitable: bool


class HabitabilityEngine:
    """
    Moteur d'évaluation astrobiologique et de recherche de biosignatures planétaires.
    """

    @classmethod
    def evaluate_habitability(cls, target_name: str = "TRAPPIST-1 e") -> HabitabilityAssessment | None:
        """
        Évalue l'habitabilité à partir du catalogue réel d'exoplanètes
        (ExoplanetDatabase), ou None si target_name n'y figure pas.

        NOTE (correction — fabricated biosignature detection): this
        used to unconditionally return the exact same fixed assessment
        - including a claimed DETECTION of "O2 (Molecular Oxygen)",
        "O3 (Ozone Shield)", "CH4 (Methane)" and "H2O Vapor"
        biosignatures with is_habitable=True - regardless of
        target_name. Claiming an actual biosignature detection (a
        landmark result in real astrobiology) as a fixed dummy value
        for any name string is one of the more dangerous fabrications
        in this codebase. No real spectroscopic pipeline is connected
        here, so detected_biosignatures is now honestly empty rather
        than claiming a detection that never happened; habitability_index_pct
        and is_habitable now come from ExoplanetDatabase's real,
        per-object ESI score and habitable-zone flag instead of a
        fixed 88.0/True for every target. liquid_water_probability_pct
        and radiation_shielding_score were invented percentages with
        no real per-object source - replaced with the catalog's own
        genuine (qualitative, not fabricated-precise) potential_water
        description; removed rather than kept as still-fabricated
        numbers.
        """
        planet = ExoplanetDatabase.get_exoplanet(target_name)
        if planet is None:
            return None

        return HabitabilityAssessment(
            target_name=planet.name,
            habitability_index_pct=round(planet.esi_score * 100.0, 1),
            potential_water=planet.potential_water,
            detected_biosignatures=[],
            is_habitable=planet.is_in_habitable_zone,
        )
