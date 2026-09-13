"""
Regression tests for the real text-clipping bug found by rendering the
AWCI dashboard at a real 1920x1080 size and looking at the actual
screenshot (2026-09-07) - not just checking scrollbar metrics.

vscroll/hscroll maximum() alone (already covered by
test_awci_dashboard_fullscreen.py) said "0 / 29px, negligible" - true
for the window as a whole, but that same 29px was enough to visually
clip the RISK SUMMARY panel's severity badges ("Extreme" rendered as
"Extrem", "Low" as "L", "Moderate" as "Moderat") and
_ComponentValueList's value column, because both are narrow, low-
stretch-factor columns that a tight Qt layout squeeze compresses
before it touches a wider sibling (the radar/route-chart matplotlib
canvases). Fixed by trimming those 2 canvases' own figsize width
(6.0->5.4in each, awci_radar.py / awci_route_chart.py) to free real
space, and giving the 2 narrow columns a real setMinimumWidth() floor
so the layout engine can no longer take that space back from them -
these tests lock in that floor.
"""

from __future__ import annotations

from acf.gui.dashboard.awci_risk_summary import AWCIRiskSummary

# NOTE (2026-09-13 refonte): self.component_list (_ComponentValueList) -
# the narrow low-stretch-factor sidebar column this regression test
# used to guard - was retired: the reference photo has no such column,
# and its real per-module drill-down is now reached via AWCIHazardRow's
# own cards instead (see awci_dashboard.py's NOTE in _build_ui()), laid
# out with an equal stretch factor each rather than as one narrow
# column squeezed against a wide matplotlib sibling - the specific
# clipping failure mode this file's own module docstring describes no
# longer applies to that removed widget. AWCIRiskSummary itself
# (tested below) is untouched and still real/reachable code, even
# though the live dashboard no longer instantiates it.


def test_risk_summary_badges_have_a_real_minimum_width_wide_enough_for_the_longest_band_name(qtbot):
    """60px, measured via QFontMetrics against the real widest band
    name ("Very High"/"Moderate", ~55px at this font) - see
    _RiskRow's own construction-time note for the full measurement."""
    summary = AWCIRiskSummary()
    qtbot.addWidget(summary)

    for _label, badge in summary._rows.values():
        assert badge.minimumWidth() >= 60
