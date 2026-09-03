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
- **`awci_dashboard_reference.jpg`** - the AWCI-specific dashboard.
  This is the SAME reference mockup `acf.gui.dashboard.awci_dashboard`
  was already built against (see that module's own docstring and
  `reports/ACF_MASTER_AUDIT_v2.md`'s "fidélité réelle à la maquette de
  référence AWCI" update) - global/regional maps, vertical
  cross-section, AWCI components radar, risk summary, route planning,
  stats bar, footer, AWCI SCALE legend, Flight Level/Rendered info
  boxes, Point Information card, Layers panel.
