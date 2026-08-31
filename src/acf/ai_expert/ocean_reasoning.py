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

        NOTE (correction): this method takes no location/time
        parameters and has no live ocean data feed wired in — it
        used to silently return fixed, realistic-looking numbers
        (SST anomaly, mixed layer depth, wave height, a literal
        "Gulf Stream speed 1.8 m/s" string) as if they were a real
        analysis, which is misleading (same class of issue as the
        fake METAR decoder and DataAssimilationEngine found earlier
        this session, though here the root cause is "no data source
        connected" rather than "wrong formula"). The values are kept
        (as illustrative placeholders, for callers/UIs that already
        expect these keys) but the dict now says explicitly that
        they are not derived from real data, rather than presenting
        them as if they were.
        """
        return {
            "sst_anomaly": "+0.8°C",
            "mixed_layer_depth_m": 45.0,
            "wave_height_hs_m": 4.5,
            "currents": "Gulf Stream speed 1.8 m/s",
            "data_source": "placeholder",
            "is_real_data": False,
        }
