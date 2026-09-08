"""
Atmospheric Complexity Framework (ACF)

Climate Intervention AI & Geoengineering Decision Engine Module (Phase 7)
(ClimateDecisionEngine implementing Observation -> Diagnosis -> Simulation -> Evaluation -> Recommendations)
"""

from typing import Any

from acf.geoengineering.solar_radiation_management import CLIMATE_SENSITIVITY_LAMBDA, SolarRadiationManagementEngine


class ClimateDecisionEngine:
    """
    Moteur de décision par IA pour l'optimisation des interventions climatiques et de la géo-ingénierie.
    """

    @classmethod
    def evaluate_intervention_strategy(cls, target_cooling_k: float = 1.0) -> dict[str, Any]:
        """
        Calcule le déploiement d'injection d'aérosols stratosphériques (SAI) requis pour
        atteindre un objectif de refroidissement donné.

        NOTE (correction — fabricated decision pipeline): every step of
        this "Observation -> Diagnosis -> Simulation -> Evaluation ->
        Recommendations" pipeline used to be a fixed narrative string
        ("DACCS (3 Gt CO2/yr) + ERW (2 Gt CO2/yr) + Moderate SAI
        (-0.5 W/m²)", "Pathway leads to Temperature Stabilization at
        +1.5°C by 2050", "IPCC AR6 / WMO Compliant Assessment Report
        Generated") returned identically no matter what target_cooling_k
        was requested - asking for 0.1 K of cooling and asking for
        10 K of cooling produced the exact same claimed simulation and
        the exact same claimed IPCC-compliant report. Only
        target_cooling_k itself was ever echoed back.

        Fix: the SAI deployment now genuinely solves
        SolarRadiationManagementEngine's own real formula
        (forcing = -0.45 * SO2, cooling = lambda * |forcing|) for the
        SO2 injection rate needed to reach target_cooling_k - real
        numbers driven by the actual input, reusing the one already-
        verified formula in this package rather than inventing a new
        one. The multi-decade temperature-stabilization pathway and
        "IPCC AR6 / WMO Compliant Assessment Report" claims required a
        real integrated assessment model this class has no access to;
        they are now honestly disclosed as not computed instead of
        asserted as fact.
        """
        so2_required_mt_yr = target_cooling_k / (CLIMATE_SENSITIVITY_LAMBDA * 0.45)
        sai_deployment = SolarRadiationManagementEngine.simulate_stratospheric_aerosol_injection(
            so2_injection_megatons_per_year=so2_required_mt_yr
        )

        return {
            "target_cooling_k": target_cooling_k,
            "required_sai_deployment": sai_deployment,
            "required_sai_so2_megatons_per_year": round(so2_required_mt_yr, 2),
            "is_real_data": True,
            "multi_decade_scenario_pathway": None,
            "scientific_report": None,
            "not_computed_note": (
                "A multi-decade temperature-stabilization pathway and a formal "
                "IPCC AR6 / WMO compliant assessment report require a real "
                "integrated assessment / climate model this engine does not "
                "have access to - not computed. Only the SAI deployment needed "
                "for the requested target_cooling_k, via the SRM engine's own "
                "formula, is real."
            ),
        }
