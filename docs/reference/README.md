# Reference dashboard mockups

Two visual reference mockups provided by the project author
(2026-09-03), accompanying [`../ACF_MASTER_PROMPT.md`](../ACF_MASTER_PROMPT.md) -
these define the intended look and information architecture for the
two real dashboards in this repository. They are reference material,
not screenshots of this codebase.

- **`acf_dashboard_reference.jpg`** - the general ACF dashboard (not
  AWCI-specific): a synoptic multi-lead-time view (T+0h/T+3h/T+6h/
  T+12h/T+24h tabs), a high-resolution complexity heatmap with a route
  overlay, a vertical cross-section, a "SCIENTIFIC DECOMPOSITION &
  EXPLAINABILITY" section (a complexity gauge, an uncertainty gauge, a
  hexagonal radar over Dynamics/Thermo/Convection/Microphysics/
  Orography/Temporal, and a dominant-couplings readout), an AWCI
  evolution time series, and a multi-model consensus/spread chart -
  matching this prompt's own §27 (Dashboard) and §29 (layer
  architecture) sections. No corresponding widget exists in
  `src/acf/gui` yet as of this writing - this is forward-looking
  reference material, not a description of current code.
- **`awci_dashboard_reference.jpg`** - REMOVED 2026-09-12 (explicit
  user request "on vas repartir a zero toutes les images du dashboard
  AWCI... suprime les"): this was the AWCI-specific mockup
  `acf.gui.dashboard.awci_dashboard` was built/pixel-matched against
  earlier in this session (global/regional maps, vertical
  cross-section, AWCI components radar, risk summary, route planning,
  stats bar, footer, AWCI SCALE legend, Flight Level/Rendered info
  boxes, Point Information card, Layers panel). The many source-code
  comments citing this file (e.g. "docs/reference/
  awci_dashboard_reference.jpg parity work") describe real,
  already-shipped design decisions made while it existed - left as-is,
  historically accurate, not rewritten just because the image itself
  is gone.
- **`awci_dashboard_reference.png`** - the CURRENT AWCI reference,
  provided 2026-09-12 (explicit user request "je veux que le dashboard
  soit exactement comme celui dans la photo... 100%... tous les
  boutons fonctionnelles"), replacing the removed `.jpg` above with a
  substantially different design: a light sidebar-navigation shell
  (Overview / Map & Visualization / Hazards / Analysis / Data &
  Reports sections) and a light top bar (Area/Date/Forecast/Model
  selectors, system status, user profile) around the SAME dark
  operational content area - global map with a Layers panel and 2D/
  3D/4D toggle, a hazard summary row (AWCI Global gauge + 6 hazard
  cards), Current Situation / Model Agreement / Airport Complexity
  cards, 5 analysis panels (Vertical Cross Section, Atmospheric
  Profile, Flight Route Analysis, Time Evolution, AWCI Vertical
  Profile), and a Recent Alerts / Latest Updates / Quick Actions
  footer row. Being built in verified phases against the real PySide6
  dashboard (`acf.gui.dashboard.awci_dashboard`) - see
  `reports/ACF_MASTER_AUDIT_v2.md` for progress.
