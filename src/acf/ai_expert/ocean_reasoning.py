"""
Atmospheric Complexity Framework (ACF)

Ocean Dynamics & Oceanography Reasoning Module
"""

from typing import Any


class OceanReasoningEngine:
    """Moteur de raisonnement océanographique."""

    @classmethod
    def analyze_ocean_state(cls) -> dict[str, Any]:
        """
        Ocean state summary.

        NOTE (correction, 2nd pass — the first correction here was
        weaker than every sibling engine in this package): this method
        takes no location/time parameters and has no live ocean data
        feed wired in. A first pass kept the original fixed, realistic-
        looking numbers (SST anomaly "+0.8°C", mixed layer depth 45.0m,
        wave height 4.5m, a literal "Gulf Stream speed 1.8 m/s" string)
        and only added an `is_real_data: False` flag next to them - a
        caller that displays the values without also checking that flag
        (nothing forces it to) would still show a specific, plausible-
        looking ocean state that was never measured, exactly the
        false-confidence risk this same package's other 8 engines
        (AviationReasoningEngine, HazardReasoningEngine,
        AIDecisionSupport, etc.) were already fixed to avoid, by nulling
        the values themselves rather than tagging them. Aligned to that
        same convention here.
        """
        return {
            "sst_anomaly": None,
            "mixed_layer_depth_m": None,
            "wave_height_hs_m": None,
            "currents": None,
            "status": "NOT_ANALYZED_NO_OCEAN_DATA_CONNECTED",
            "is_real_data": False,
        }
