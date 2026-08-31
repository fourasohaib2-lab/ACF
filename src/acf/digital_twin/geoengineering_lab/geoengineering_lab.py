"""
Atmospheric Complexity Framework (ACF)

Geoengineering Experiment Laboratory Module (Phase 6)
"""

from typing import Any


class GeoengineeringLab:
    """Laboratoire d'expérimentation de la géo-ingénierie et de modification du bilan radiatif."""

    @classmethod
    def simulate_stratospheric_aerosol_injection(cls, sasi_amount_mt_so2: float = 5.0) -> dict[str, Any]:
        """
        Simule l'injection de dioxyde de soufre dans la stratosphère (SAI).

        NOTE (correction): this used to ignore sasi_amount_mt_so2's
        value (beyond echoing it) and unconditionally claim a fixed
        "-0.45K cooling" and "4.2 benefit-cost ratio" regardless of
        the injection amount - physically wrong (a real climate
        response scales with injection amount) as well as fabricated
        (no climate model is connected here). The side_effects list
        quoted specific fabricated impact percentages (e.g. "-12%
        South Asian Monsoon Rainfall") as if from a real simulation.
        Geoengineering is a genuinely contested policy topic - a fake
        "4.2 benefit-cost ratio" could misinform a real policy
        argument. Not fabricated: the qualitative risk categories
        (monsoon disruption, ozone recovery delay, termination shock)
        are well-documented in the SAI literature in general terms and
        are kept as known risk categories, not simulation output.
        """
        return {
            "technique": "Stratospheric Aerosol Injection (SAI)",
            "injection_so2_mt_yr": sasi_amount_mt_so2,
            "cooling_effect_k": None,
            "known_risk_categories": [
                "Regional monsoon precipitation disruption (documented in SAI literature)",
                "Delayed stratospheric ozone recovery (documented in SAI literature)",
                "Termination shock risk upon abrupt cessation (documented in SAI literature)",
            ],
            "benefit_cost_ratio": None,
            "status": "NOT_SIMULATED_NO_CLIMATE_MODEL_CONNECTED",
            "is_real_data": False,
        }
