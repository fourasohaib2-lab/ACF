"""
Atmospheric Complexity Framework (ACF)

Synoptic Scale Meteorological Analyzer Module
"""

from typing import Any


class SynopticAnalyzer:
    """Analyseur de grande échelle (synoptique)."""

    @classmethod
    def analyze_synoptic_chart(cls) -> dict[str, Any]:
        """
        NOTE (correction): this used to unconditionally claim fixed
        fabricated synoptic features ("Icelandic Low (982 hPa)", "Azores
        High (1028 hPa)"...) for ANY call, with 0 parameters and no real
        surface analysis/reanalysis chart connected. Not fabricated.
        """
        return {
            "scale": "Synoptic (1000 km - 5000 km)",
            "patterns": [],
            "jet_stream": None,
            "status": "NOT_ANALYZED_NO_SYNOPTIC_CHART_CONNECTED",
            "is_real_data": False,
        }
