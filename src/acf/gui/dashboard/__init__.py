"""
ACF - Dashboard Module
======================

AWCI Dashboard widgets.

AUDIT NOTE (2026-09-06, Tier C sweep): 52 files, 38 already carried an
explicit disclosure before this pass. The 14 that didn't were read in
full here (acf_workstation_command_palette.py, _map_inspector.py,
_overview_landing.py, _sounding_panel.py, _thumbnail_strip.py,
_window.py, awci_colors.py, awci_decomposition.py,
awci_evolution_chart.py, awci_footer.py, awci_gauge.py,
awci_messages_panel.py, awci_radar.py, awci_stats_bar.py) - all either
already carried a disclosure note this sweep's own grep pattern missed
(e.g. the "RÈGLE D'OR" phrasing used for dead-but-correct widgets like
AWCIDecomposition/AWCIGauge) or were genuinely clean: real live data
(awci_messages_panel.py's METAR/TAF/SIGMET feed, awci_evolution_chart.
py's real AWCI(t) trajectory), and awci_footer.py's own UI text
honestly labels the dashboard "SYNTHETIC VIEW" / "RESEARCH STAGE -
Prototype - To be validated". Nothing new to disclose.
"""

from .awci_dashboard import AWCIDashboard
from .awci_decomposition import AWCIDecomposition
from .awci_gauge import AWCIGauge
from .awci_timeline import AWCITimeline
from .awci_vertical_profile import AWCIVerticalProfile

__all__ = [
    "AWCIDashboard",
    "AWCIDecomposition",
    "AWCIGauge",
    "AWCITimeline",
    "AWCIVerticalProfile",
]
