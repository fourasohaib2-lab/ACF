"""
Atmospheric Complexity Framework (ACF)

Reports - Generator

Real re-export of ``acf.reports.generator``. This module originally
held its own real implementation (built here first, for the AWCI
aviation report); once the same real, generic need was recognized
beyond that one caller, it was promoted to ``acf.reports`` - this
module now reuses that one, not a second, duplicate implementation.
"""

from __future__ import annotations

from acf.reports.generator import ReportSection, render_report

__all__ = ["ReportSection", "render_report"]
