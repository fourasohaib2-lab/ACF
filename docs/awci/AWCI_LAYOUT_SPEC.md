# AWCI Layout Specification

**Date:** 2026-09-03. This is a Qt `QVBoxLayout`/`QHBoxLayout` tree (not
CSS/flexbox) — the real layout `AWCIDashboard._build_ui()` builds. Values
are Qt stretch factors and pixel minimums actually set in source, not
estimated from a screenshot (the master prompt's "measure x/y/width/height
from the image" instruction does not apply to a Qt layout, which is
resolution-independent by construction — the real geometry values below
are the ones that matter for THIS stack).

```
AWCIDashboard (QVBoxLayout, margins 10/10/10/0, spacing 8)
├─ header_row (QHBoxLayout)
│   ├─ title QLabel ("AWCI – AVIATION WEATHER COMPLEXITY INDEX")
│   ├─ stretch
│   ├─ 🔬 Real Physics / ▶ Play Evolution / 🧊 3D View / 📨 Message / 🔔 Alerts buttons
│   └─ status badge QLabel (RESEARCH STAGE)
├─ subheader QLabel ("Concept Output – Research Prototype")
├─ view_mode_row (QHBoxLayout) — VIEW MODE: 3 QRadioButtons, stretch,
│   "Flight Level:" QLabel + flight_level_selector QComboBox (built this
│   closure — real single source of truth for the point-of-interest
│   pipeline's flight level, see AWCI_INTERACTION_MATRIX.md)
├─ row1 (QHBoxLayout, stretch=3 in outer)
│   ├─ global_map AWCIMapPanel, stretch=3, setMinimumHeight(340)
│   └─ right_col (QVBoxLayout, stretch=2)
│       ├─ cross_section AWCICrossSection, stretch=1, setMinimumHeight(220)
│       └─ radar_row (QHBoxLayout, stretch=1)
│           ├─ radar AWCIRadar, stretch=2
│           └─ component_list _ComponentValueList, stretch=1
├─ stats_bar AWCIStatsBar (5 boxes incl. half-circle gauge)
├─ row2 (QHBoxLayout, stretch=2 in outer)
│   ├─ left_col2 (QVBoxLayout, stretch=3)
│   │   ├─ regional_map AWCIMapPanel, stretch=1, setMinimumHeight(260)
│   │   ├─ regional_extras_row (QHBoxLayout) — AWCITimeline sparkline + 🔍 See Vertical Profile button
│   │   ├─ time_row (QHBoxLayout) — "Valid Time:" + QSlider(0-23) + readout
│   │   └─ level_row (QHBoxLayout) — "Level:" + QSlider + readout
│   └─ right_col2 (QVBoxLayout, stretch=2)
│       ├─ op_header QLabel ("AWCI – OPERATIONAL USE EXAMPLE")
│       ├─ op_row (QHBoxLayout, stretch=1)
│       │   ├─ route_chart AWCIRouteChart, stretch=2
│       │   └─ risk_summary AWCIRiskSummary, stretch=1
│       ├─ compare_fl_button QPushButton
│       └─ recommendation_banner QLabel (hidden unless something is elevated)
└─ footer AWCIFooter (5 cells)
```

## Real regression this spec documents

A real layout-collapse bug was found and fixed while verifying the
previous closure: the new fixed-height widgets added to `row2`
(sparkline, banner, VIEW MODE row) competed with `row1`'s stretch factor
in Qt's layout algorithm and collapsed `global_map` to ~157px tall (was
425px). Fixed via the explicit `setMinimumHeight()` calls listed above —
the same fix pattern already used once before this session
(`acf_general_dashboard.py`). Any future addition of a fixed-height
widget anywhere in this tree should re-verify `global_map`/`regional_map`/
`cross_section` heights by screenshot before considering the change done.

## Design tokens (real, `acf.gui.theme_tokens.TOKENS`)

Background `#0b1220`/`#0f1830`/`#16213e`, border `#263450`, text
`#e8edf5`/`#9fb0c9`/`#6b7a94`, AWCI scale colors
(`acf.gui.dashboard.awci_colors.LEVELS`): Very Low `rgb(0,200,100)`, Low
`rgb(100,200,50)`, Moderate `rgb(255,200,0)`, High `rgb(255,150,0)`, Very
High `rgb(255,100,0)`, Extreme `rgb(255,0,0)`. These are the single
source of truth reused by the map legend, cross-section colorbar, risk
badges, gauge bands, and stats-bar coloring — never redefined locally
per-widget.
