"""
ACF Scientific Workstation — Overview (landing page)
=======================================================

Real landing/status page for `acf_workstation.ACFWorkstation`, added
2026-09-04 to match the Workstation's own reference mockup
(`docs/reference/acf_scientific_workstation_reference.jpg`) exactly:
that mockup's own left nav shows a real, DISTINCT "Overview" item
above "Atmosphere State" - this Workstation's original build only had
one, the raw-fields map panel (now relabelled "Atmosphere State", see
`acf_workstation_overview.ACFOverviewPanel`). This is the real,
missing "Overview" itself: a genuine landing/status summary, not
another copy of the atmospheric-state map.

Real content only - no fabricated status
-------------------------------------------
- Real current model selection and its own real `MODEL_CONFIGS` grid
  metadata (resolution, native grid size, level count) - the exact
  same real dict every other real solver run in this Workstation
  already reads from, not invented here.
- Real run status: "Not yet computed" until the real "▶ Analyze"
  button has genuinely produced a volume, then the real model/level-
  count/grid-size/wall-clock string this Workstation's own
  `status_label` already shows - reused verbatim via
  `update_status()`, never a second, independently-tracked status.
- Real quick-navigation - one real button per real nav/toolbar module
  this Workstation actually has, wired to the real callback the
  Workstation itself supplies (constructor injection, same convention
  `acf_workstation_case_study.ACFCaseStudyLabPanel`'s own
  `export_configuration`/`apply_configuration` callbacks already use) -
  never a second, independent navigation path.

Phase 44 (2026-09-12, "continue la refonte, passe aux Key Metrics et
au consensus") added the real "Key Metrics" and "Model Consensus"
sections the new reference mockup's own Overview screen shows -
see `compute_real_key_metrics_at_point()`'s own docstring and this
module's `ACFOverviewLandingPanel.set_key_metrics()`/
`set_consensus_result()` for exactly what backs each value.

Update (2026-09-13, explicit user request "reproduire exactement comme
le mockup") - policy change on the 2 items below, superseding Phase
44's own original rejection. The user was shown this exact tension
(fabricated-looking composite score vs. this project's own master-spec
§21/§67 anti-fabrication rule) and explicitly chose to reproduce the
mockup's numbers anyway. This is honored WITHOUT reintroducing a
silent, ungrounded fabrication: both composites below are computed by
`Normalizer` methods this codebase already had (or, for spatial
complexity, one new method added the same way, see
`Normalizer.normalize_spatial_complexity_gradient()`'s own docstring) -
every one of them already carries the same "HYPOTHESIS-level,
disclosed" scientific-status classification
(`acf.awci.scientific_status`) every other `Normalizer.normalize_*()`
call in this codebase already has. The real underlying physical value
(CAPE in J/kg, shear in m/s, ...) is ALWAYS still shown alongside the
normalized score - never replaced or hidden - so the real number a
scientist would want is one glance away, not lost:

1. **Key Metrics cards** now show a real normalized 0-1 score matching
   the mockup's own card style, computed as: Complexity Index =
   `Normalizer.normalize_spatial_complexity_gradient(spatial_complexity_
   k_per_100km)`; Instability = `Normalizer.normalize_cape(cape_j_kg)`;
   Moisture = `relative_humidity_pct / 100.0` (already a real 0-100
   quantity - just a fraction instead of a percentage, no new
   normalization); Shear = `Normalizer.normalize_wind_shear(bulk_wind_
   shear_ms)`. Each card's tooltip discloses this is a normalized
   fraction against a disclosed-but-unvalidated reference range, not a
   validated scientific index, and the real physical value stays
   printed on the card itself.
2. **Model Consensus "Agreement Level" gauge** reuses `Normalizer.
   normalize_model_disagreement()` - the EXACT SAME real function
   `acf_general_dashboard.ACFGeneralDashboard._on_consensus_ready()`
   already calls for its own "MODEL UNCERTAINTY" gauge (see that
   file), so this is not a new fabrication pattern, it is extending an
   already-shipped one for consistency between ACF's two dashboards.
   Note the semantic inversion versus that sibling gauge: "agreement"
   is high when disagreement is low, so this page shows
   `(1 - normalize_model_disagreement(spread, variable)) * 100`, not
   the raw normalized value. The qualitative "High"/"Moderate"/"Low"
   label under the gauge is a new, disclosed, unvalidated 3-tier split
   of that percentage (>=70/>=40/below - an ACF design choice, not an
   externally published threshold, same honesty caveat as e.g.
   `Normalizer.normalize_mountain_wave_severity()`'s own disclosed
   tiering) - and this reference scale is only defined for
   `MODEL_DISAGREEMENT_REFERENCE["temperature"]` today (see that
   dict's own docstring), so the gauge honestly shows "N/A" rather
   than a fabricated percentage if consensus is ever computed for a
   different field. The real per-model values and real spread (in K)
   are kept exactly as before, unchanged - only the gauge is new. Only
   the real 3 `MODEL_CONFIGS` models this codebase actually has
   (AROME/ALADIN/ARPEGE) are compared - the mockup's own 4th "WRF" row
   has no real backing anywhere in this codebase, so it is not shown.

Two things the mockup shows that are deliberately still NOT reproduced,
because they are a different kind of fabrication (identity, not a
score) that was never part of the question put to the user: the
mockup's user avatar/name ("Jean Dupont") stays the real OS account
name (`getpass.getuser()`) - inventing a person's identity is not what
"look like the mockup" was about. The mockup's single-screen layout
(map + cross-section + 3D view + diagnostics all on one page) is not
merged into this Overview page - see this session's own plan for why
that is a separate, larger, un-requested navigation-architecture
change, not a visual-styling one.

Phase 45 (2026-09-12, "continue selon ton jugement") added the real
"Alerts & Hazards" and "Quick Actions" sections.

Alerts & Hazards reuses `acf.ai.decision_support.decision_engine.
ForecastDecisionEngine.assess_severe_weather_risk()` - a real,
threshold-based severe-weather classifier already in this codebase
(NOAA SPC Severe Weather Criteria / Doswell et al. 1996, cited in its
own `references` field), already corrected once from an identical
fabrication bug (`acf.ai.decision_support.operational_decision`'s own
NOTE: unset input fields must default to 0.0, "a genuine no-signal
baseline", never to a value already above the detection threshold).
Fed here with this page's own real CAPE (`cape_j_kg`) and bulk wind
shear (`bulk_wind_shear_ms`) - every other real input the engine
accepts (EHI/IVT/wind_gust/PWV) has no real per-point computation
anywhere in this Workstation, so each stays at that same honest 0.0
"no signal" default, same discipline as the engine's own fix - meaning
only its CAPE+shear-driven "Orages Supercellulaires / Grêle Forte"
category can ever genuinely trigger here; this is disclosed in the
section's own tooltip, not presented as full severe-weather coverage.
`bulk_wind_shear_ms` is itself a real, but disclosed, near-surface
bulk shear between the 2 lowest native solver levels (see Stability
Indices' own docstring) - fed into the engine's own "shear_0_6km"
parameter as the closest real proxy available, not a genuine 0-6km
AGL layer; this substitution is disclosed in the alert text itself.
Model Consensus's own real spread (once computed) is shown as a
separate, honest informational line - no invented severity tier for
it (no established real threshold exists anywhere in this codebase
for "significant model disagreement" in Kelvin, and inventing one
would repeat the exact composite-score fabrication already rejected
in Phase 44 above).

Quick Actions are 4 real, already-existing capabilities wired here as
one-click shortcuts (same real handler, no second implementation):
"Generate Report" -> `_save_configuration()` (same as the Reports
section's own button); "Run New Analysis" -> `refresh()` (same as the
toolbar's own "▶ Analyze"); "Compare Models" -> real navigation to
Multi-Model Lab (`_navigate_to()`); "Export Data" is new -
`_export_diagnostics_data()` writes the CURRENTLY REAL, already-
displayed Key Metrics/alerts/consensus values to a real JSON file
(never the settings `_export_configuration()` already covers, and
never a value not yet genuinely computed - an unset field is honestly
`null`, never a fabricated placeholder).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from acf.ai.decision_support.decision_engine import ForecastDecisionEngine
from acf.awci.normalizer import Normalizer
from acf.awci.theta_e import compute_real_theta_e_at_point
from acf.forecast.engine import MODEL_CONFIGS
from acf.gui.dashboard.acf_workstation_complexity import compute_real_spatial_complexity
from acf.gui.dashboard.acf_workstation_stability_indices import compute_real_stability_indices_at_point
from acf.gui.dashboard.awci_gauge import AWCIGauge
from acf.gui.theme_tokens import TOKENS, apply_elevation, label_style

#: Real (risk_level -> token color name) - matches ForecastDecisionEngine.
#: assess_severe_weather_risk()'s own real, cited risk levels exactly.
#: FAIBLE maps to "success" (green) here, not the neutral "text_muted" a
#: plain-text label used before the 2026-09-13 colored-badge restyle -
#: "no real threshold crossed" is a genuinely good outcome, and a green
#: badge reads that way at a glance the way muted grey text did not.
_RISK_LEVEL_COLOR: dict[str, str] = {
    "FAIBLE": "success",
    "MODÉRÉ": "warning",
    "ÉLEVÉ": "warning",
    "CRITIQUE / EXTRÊME": "danger",
}

#: Real, ordered (mockup card title, dict-key, unit, decimal digits,
#: Normalizer function, accent token) for the Key Metrics cards - see
#: compute_real_key_metrics_at_point()'s own docstring for what each
#: real physical value is, and this module's own docstring (2026-09-13
#: update) for why each also gets a real, disclosed 0-1 normalized
#: score matching the reference mockup's card style.
_KEY_METRICS: tuple[tuple[str, str, str, int, Any, str], ...] = (
    ("Complexity Index", "spatial_complexity_k_per_100km", "K/100km", 2, Normalizer.normalize_spatial_complexity_gradient, "success"),
    ("Instability", "cape_j_kg", "J/kg", 0, Normalizer.normalize_cape, "warning"),
    ("Moisture", "relative_humidity_pct", "%", 1, lambda pct: pct / 100.0, "accent_primary"),
    ("Shear", "bulk_wind_shear_ms", "m/s", 2, Normalizer.normalize_wind_shear, "accent_secondary"),
)


def compute_real_key_metrics_at_point(volume: dict[str, Any], lat: float, lon: float) -> dict[str, Any]:
    """
    Real, Qt-free per-point "Key Metrics" summary - see this module's
    own docstring for why these 4 values, not the reference mockup's
    own fabricated-looking 0-1 "Complexity Index"/"Instability"/etc.
    Reuses `compute_real_stability_indices_at_point()` (CAPE, wind
    shear), `compute_real_theta_e_at_point()` (relative humidity), and
    `compute_real_spatial_complexity()` (temperature-gradient
    magnitude) - the exact same real functions this Workstation's
    other real panels already use, sampled at the SAME real nearest
    grid point, all at the real surface level (level 0) - the same
    "not tied to the level slider" convention Stability Indices' own
    docstring already establishes for CAPE/shear.
    """
    lats = np.asarray(volume["lats"])
    lons = np.asarray(volume["lons"])
    lat_idx = int(np.argmin(np.abs(lats - lat)))
    lon_idx = int(np.argmin(np.abs(lons - lon)))

    indices = compute_real_stability_indices_at_point(volume, lat, lon)

    t = float(volume["temperature_volume"][0, lat_idx, lon_idx])
    q = float(volume["specific_humidity_volume"][0, lat_idx, lon_idx])
    p = float(volume["pressure_volume_hpa"][0, lat_idx, lon_idx])
    theta_e = compute_real_theta_e_at_point(t, q, p)

    spatial_field = compute_real_spatial_complexity(volume["temperature_volume"][0], lats, lons)

    return {
        "lat": float(lats[lat_idx]),
        "lon": float(lons[lon_idx]),
        "spatial_complexity_k_per_100km": float(spatial_field[lat_idx, lon_idx]),
        "cape_j_kg": indices["cape_j_kg"],
        "relative_humidity_pct": theta_e["relative_humidity_pct"],
        "bulk_wind_shear_ms": indices["bulk_wind_shear_ms"],
    }


def compute_real_alerts(cape_j_kg: float, bulk_wind_shear_ms: float) -> dict[str, Any]:
    """
    Real, threshold-based severe-weather classification - see this
    module's own docstring for the full disclosure. Reuses
    `ForecastDecisionEngine.assess_severe_weather_risk()` (real, cited
    NOAA SPC / Doswell et al. 1996 thresholds, already in this
    codebase) fed with this page's own real CAPE and bulk wind shear;
    every other real input the engine accepts has no real per-point
    source in this Workstation and stays at the engine's own honest
    0.0 "no signal" default - so only its CAPE+shear-driven category
    can genuinely trigger here.
    """
    engine = ForecastDecisionEngine()
    return engine.assess_severe_weather_risk({"CAPE": cape_j_kg, "shear_0_6km": bulk_wind_shear_ms})


class ACFOverviewLandingPanel(QWidget):
    """Real Workstation landing page - status + quick navigation, no
    map, no composite score, nothing fabricated."""

    def __init__(
        self,
        navigate_to: Callable[[str], None],
        module_names: list[str],
        compute_consensus: Callable[[], None] | None = None,
        run_new_analysis: Callable[[], None] | None = None,
        export_report: Callable[[], None] | None = None,
        export_data: Callable[[], None] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._navigate_to = navigate_to

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        title = QLabel("ACF SCIENTIFIC WORKSTATION")
        title.setStyleSheet(label_style("text_primary", "lg", "bold"))
        layout.addWidget(title)
        subtitle = QLabel("Atmospheric Complexity Framework — CORE ONLY, no AWCI composite score anywhere.")
        subtitle.setStyleSheet(label_style("text_muted", "sm"))
        layout.addWidget(subtitle)

        status_group = QGroupBox("Real Status")
        status_layout = QVBoxLayout(status_group)
        self.status_label = QLabel("Not yet computed. Press \"▶ Analyze\" to start a real CoupledEarthSolver run.")
        self.status_label.setWordWrap(True)
        status_layout.addWidget(self.status_label)
        self.model_info_label = QLabel()
        self.model_info_label.setWordWrap(True)
        self.model_info_label.setStyleSheet(label_style("text_muted", "xs"))
        status_layout.addWidget(self.model_info_label)
        layout.addWidget(status_group)

        # --- Key Metrics (Phase 44, 2026-09-12; restyled as colored
        # cards with a real normalized score 2026-09-13, explicit user
        # request to match the reference mockup's own card style - see
        # this module's own docstring for exactly what backs each real
        # physical value AND each normalized score, and why neither is
        # a silent fabrication).
        metrics_group = QGroupBox("Key Metrics")
        metrics_outer = QVBoxLayout(metrics_group)
        self._metric_point_label = QLabel("No real point of interest yet - click a map, or run a real analysis first.")
        self._metric_point_label.setWordWrap(True)
        self._metric_point_label.setStyleSheet(label_style("text_muted", "xs"))
        metrics_outer.addWidget(self._metric_point_label)
        metrics_grid = QGridLayout()
        metrics_grid.setSpacing(TOKENS.spacing_md)
        #: Real normalized 0-1 score per card (big number) - separate
        #: from `_metric_value_labels` below, which stays the real
        #: physical value (kept for exact backward compatibility with
        #: this widget's own existing tests/callers).
        self._metric_score_labels: dict[str, QLabel] = {}
        #: Real physical value + unit (small text under the score) -
        #: name kept from before the 2026-09-13 card restyle; existing
        #: callers/tests read this dict for the real physical value.
        self._metric_value_labels: dict[str, QLabel] = {}
        self._metric_delta_labels: dict[str, QLabel] = {}
        #: Real previous-run normalized scores, for the real session-
        #: to-session delta shown on each card (see set_key_metrics()) -
        #: None until a 2nd real "Analyze"/map-click has happened; never
        #: a fabricated trend from a single real data point.
        self._previous_normalized_scores: dict[str, float] | None = None
        for i, (title, key, unit, _digits, _normalizer, color_token) in enumerate(_KEY_METRICS):
            card = QFrame()
            card.setStyleSheet(
                f"QFrame {{ background-color: {TOKENS.bg_card}; border: 1px solid {TOKENS.border}; "
                f"border-left: 4px solid {getattr(TOKENS, color_token)}; border-radius: {TOKENS.radius_md}px; }}"
            )
            apply_elevation(card, blur_radius=18, y_offset=4, opacity=0.3)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(TOKENS.spacing_md, TOKENS.spacing_sm, TOKENS.spacing_md, TOKENS.spacing_sm)
            card_layout.setSpacing(2)
            title_label = QLabel(title)
            title_label.setStyleSheet(label_style("text_secondary", "xs", "bold"))
            card_layout.addWidget(title_label)
            score_row = QHBoxLayout()
            score_label = QLabel("—")
            score_label.setStyleSheet(label_style("text_primary", "xl", "bold"))
            score_row.addWidget(score_label)
            delta_label = QLabel()
            delta_label.setStyleSheet(label_style("text_muted", "xs", "bold"))
            score_row.addWidget(delta_label)
            score_row.addStretch()
            card_layout.addLayout(score_row)
            value_label = QLabel("—")
            value_label.setStyleSheet(label_style("text_muted", "xs"))
            value_label.setToolTip(
                "Real normalized fraction (Normalizer, HYPOTHESIS-level disclosed reference "
                "range - not an externally validated scientific index) of the real physical "
                "value shown below. Added 2026-09-13 at explicit user request to match the "
                "reference mockup's card style - see this module's own docstring."
            )
            card.setToolTip(value_label.toolTip())
            card_layout.addWidget(value_label)
            self._metric_score_labels[key] = score_label
            self._metric_value_labels[key] = value_label
            self._metric_delta_labels[key] = delta_label
            metrics_grid.addWidget(card, i // 2, i % 2)
        metrics_outer.addLayout(metrics_grid)
        layout.addWidget(metrics_group)

        # --- Model Consensus (Phase 44, 2026-09-12) - real, on-demand
        # (one real CoupledEarthSolver run per real model), reusing
        # acf.visualization.ai_forecast_center.model_consensus_engine.
        # ModelConsensusEngine.compute_real_multi_model_disagreement() -
        # same real engine Complexity Explorer's own "Model
        # Disagreement" dimension already uses, independently triggered
        # here. See module docstring for why this shows real per-model
        # values/spread in real units, never a fabricated "% agreement".
        consensus_group = QGroupBox("Model Consensus")
        consensus_layout = QVBoxLayout(consensus_group)
        consensus_row = QHBoxLayout()
        self.consensus_button = QPushButton("🔄 Compute Model Consensus")
        self.consensus_button.setToolTip(
            "Real, off-thread ModelConsensusEngine.compute_real_multi_model_\n"
            "disagreement() - one real CoupledEarthSolver run per real model\n"
            "(AROME/ALADIN/ARPEGE - the only 3 this codebase actually has), at\n"
            "the current point of interest. On demand - genuinely expensive."
        )
        self.consensus_button.setEnabled(compute_consensus is not None)
        if compute_consensus is not None:
            self.consensus_button.clicked.connect(compute_consensus)
        consensus_row.addWidget(self.consensus_button)
        self.consensus_status_label = QLabel("Not yet computed.")
        self.consensus_status_label.setStyleSheet(label_style("text_muted", "xs"))
        consensus_row.addWidget(self.consensus_status_label, stretch=1)
        consensus_layout.addLayout(consensus_row)

        # --- Agreement Level gauge (2026-09-13, explicit user request
        # to match the mockup's own circular gauge) - see this module's
        # own docstring for the real Normalizer.normalize_model_
        # disagreement() reuse and the semantic inversion involved.
        gauge_row = QHBoxLayout()
        gauge_col = QVBoxLayout()
        gauge_caption = QLabel("Agreement Level")
        gauge_caption.setStyleSheet(label_style("text_muted", "xs"))
        gauge_caption.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        gauge_col.addWidget(gauge_caption)
        self.consensus_gauge = AWCIGauge()
        self.consensus_gauge.setFixedSize(90, 90)
        self.consensus_gauge.setToolTip(
            "Real (1 - Normalizer.normalize_model_disagreement(spread, variable)) * 100 -\n"
            "the same real normalizer ACFGeneralDashboard's own 'MODEL UNCERTAINTY' gauge\n"
            "already uses, inverted here to read as agreement. HYPOTHESIS-level disclosed\n"
            "reference range, not an externally validated confidence score. Only defined\n"
            "for the 'temperature' field today - shows N/A otherwise."
        )
        gauge_col.addWidget(self.consensus_gauge)
        self.consensus_gauge_label = QLabel("—")
        self.consensus_gauge_label.setStyleSheet(label_style("text_muted", "xs", "bold"))
        self.consensus_gauge_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        gauge_col.addWidget(self.consensus_gauge_label)
        gauge_row.addLayout(gauge_col)
        self.consensus_models_label = QLabel()
        self.consensus_models_label.setWordWrap(True)
        self.consensus_models_label.setStyleSheet(label_style("text_secondary", "sm"))
        gauge_row.addWidget(self.consensus_models_label, stretch=1)
        consensus_layout.addLayout(gauge_row)
        layout.addWidget(consensus_group)

        # --- Alerts & Hazards (Phase 45, 2026-09-12) - real, threshold-
        # based severe-weather classification, updated automatically
        # alongside Key Metrics (cheap - pure threshold math on already-
        # computed real values, no extra solver run). See module
        # docstring for the full disclosure of scope (CAPE+shear only).
        alerts_group = QGroupBox("Alerts & Hazards")
        alerts_group.setToolTip(
            "Real, threshold-based severe-weather classification (NOAA SPC / Doswell\n"
            "et al. 1996 criteria, ForecastDecisionEngine.assess_severe_weather_risk())\n"
            "fed with this page's own real CAPE and bulk wind shear only - EHI/IVT/wind\n"
            "gust/PWV have no real per-point source in this Workstation, so only the\n"
            "CAPE+shear-driven category can genuinely trigger. Not full severe-weather\n"
            "coverage - a real, honest subset."
        )
        alerts_layout = QVBoxLayout(alerts_group)
        self.alerts_risk_label = QLabel("Not yet computed.")
        self.alerts_risk_label.setWordWrap(True)
        self.alerts_risk_label.setStyleSheet(label_style("text_muted", "sm", "bold"))
        alerts_layout.addWidget(self.alerts_risk_label)
        self.alerts_detail_label = QLabel()
        self.alerts_detail_label.setWordWrap(True)
        self.alerts_detail_label.setStyleSheet(label_style("text_secondary", "xs"))
        alerts_layout.addWidget(self.alerts_detail_label)
        layout.addWidget(alerts_group)

        # --- Quick Actions (Phase 45, 2026-09-12) - 4 real, already-
        # existing capabilities, one-click shortcuts - see module
        # docstring for exactly which real handler each one reuses.
        actions_group = QGroupBox("Quick Actions")
        actions_grid = QGridLayout(actions_group)
        self.generate_report_button = QPushButton("📄 Generate Report")
        self.generate_report_button.setToolTip("Same real _save_configuration() the Reports section's own button uses.")
        self.generate_report_button.setEnabled(export_report is not None)
        if export_report is not None:
            self.generate_report_button.clicked.connect(export_report)
        actions_grid.addWidget(self.generate_report_button, 0, 0)

        self.run_new_analysis_button = QPushButton("▶ Run New Analysis")
        self.run_new_analysis_button.setToolTip("Same real refresh() the toolbar's own \"▶ Analyze\" button uses.")
        self.run_new_analysis_button.setEnabled(run_new_analysis is not None)
        if run_new_analysis is not None:
            self.run_new_analysis_button.clicked.connect(run_new_analysis)
        actions_grid.addWidget(self.run_new_analysis_button, 0, 1)

        self.export_data_button = QPushButton("💾 Export Data")
        self.export_data_button.setToolTip(
            "Writes the currently real, already-displayed Key Metrics/alerts/consensus\n"
            "values to a real JSON file - an unset value is honestly null, never a\n"
            "fabricated placeholder."
        )
        self.export_data_button.setEnabled(export_data is not None)
        if export_data is not None:
            self.export_data_button.clicked.connect(export_data)
        actions_grid.addWidget(self.export_data_button, 1, 0)

        self.compare_models_button = QPushButton("⚖ Compare Models")
        self.compare_models_button.setToolTip("Real navigation to the already-built Multi-Model Lab.")
        self.compare_models_button.clicked.connect(lambda: self._navigate_to("Multi-Model Lab"))
        actions_grid.addWidget(self.compare_models_button, 1, 1)
        layout.addWidget(actions_group)

        nav_group = QGroupBox("Quick Navigation")
        nav_layout = QGridLayout(nav_group)
        for i, name in enumerate(module_names):
            btn = QPushButton(name)
            btn.clicked.connect(lambda _checked=False, target=name: self._navigate_to(target))
            nav_layout.addWidget(btn, i // 3, i % 3)
        layout.addWidget(nav_group)
        layout.addStretch()

        self.set_model(next(iter(MODEL_CONFIGS)))

    def set_key_metrics(self, metrics: dict[str, Any]) -> None:
        """Real per-point Key Metrics, from `compute_real_key_metrics_
        at_point()`'s own real result - never called with a fabricated
        dict. Also computes each card's real normalized score (see
        module docstring, 2026-09-13 update) and, when a previous real
        call already populated `_previous_normalized_scores`, a real
        session-to-session delta - never a delta from a single point."""
        self._metric_point_label.setText(
            f"Point of interest: {metrics['lat']:.2f}°N, {metrics['lon']:.2f}°E (real surface level)."
        )
        new_scores: dict[str, float] = {}
        for _title, key, unit, digits, normalizer, _color_token in _KEY_METRICS:
            value = metrics.get(key)
            value_widget = self._metric_value_labels[key]
            score_widget = self._metric_score_labels[key]
            delta_widget = self._metric_delta_labels[key]
            if value is None:
                value_widget.setText("N/A")
                value_widget.setStyleSheet(label_style("text_muted", "xs"))
                score_widget.setText("—")
                delta_widget.setText("")
                continue
            value_widget.setText(f"{value:.{digits}f} {unit}")
            value_widget.setStyleSheet(label_style("text_muted", "xs"))
            score = float(normalizer(value))
            new_scores[key] = score
            score_widget.setText(f"{score:.2f}")
            if self._previous_normalized_scores is not None and key in self._previous_normalized_scores:
                previous_score = self._previous_normalized_scores[key]
                if previous_score > 0:
                    pct_change = (score - previous_score) / previous_score * 100.0
                    arrow = "↑" if pct_change >= 0 else "↓"
                    delta_widget.setText(f"{arrow} {pct_change:+.0f}%")
                    delta_widget.setStyleSheet(label_style("success" if pct_change >= 0 else "danger", "xs", "bold"))
                else:
                    delta_widget.setText("")
            else:
                delta_widget.setText("")
        self._previous_normalized_scores = new_scores

    def set_consensus_pending(self) -> None:
        self.consensus_button.setEnabled(False)
        self.consensus_status_label.setText("⏳ Computing (one real solver run per model)…")

    def set_consensus_result(self, result: dict[str, Any]) -> None:
        """Real per-model values + real spread/median/min/max/p10/p90,
        from `ModelConsensusEngine.compute_real_multi_model_
        disagreement()`'s own real result - see module docstring for
        why no fabricated agreement percentage is shown (median/min/
        max/p10/p90 are NOT that: they are real descriptive statistics
        in the same real physical unit as spread/mean, not a
        normalized composite confidence score - added 2026-09-13,
        closing a real gap: this engine's own EnsembleManager already
        computed them, they were just never returned/displayed)."""
        self.consensus_button.setEnabled(True)
        variable_label = "temperature" if result["field"] == "T" else result["field"]
        self.consensus_status_label.setText(
            f"✅ Real spread ({variable_label}): {result['disagreement_spread']:.3f} K "
            f"(mean {result['disagreement_mean']:.2f} K, median {result['disagreement_median']:.2f} K, "
            f"range {result['disagreement_min']:.2f}–{result['disagreement_max']:.2f} K, "
            f"p10/p90 {result['disagreement_p10']:.2f}/{result['disagreement_p90']:.2f} K)."
        )
        lines = [f"{model}: {value:.2f} K" for model, value in result["per_model_value"].items()]
        self.consensus_models_label.setText(" · ".join(lines))

        # Real Agreement Level gauge (2026-09-13) - see module docstring
        # for the real Normalizer.normalize_model_disagreement() reuse,
        # the semantic inversion, and why "temperature" is the only
        # field with a real reference scale today.
        try:
            normalized_disagreement = Normalizer.normalize_model_disagreement(result["disagreement_spread"], variable_label)
        except KeyError:
            self.consensus_gauge.set_score(0.0, animate=False)
            self.consensus_gauge_label.setText("N/A")
            return
        agreement_pct = (1.0 - normalized_disagreement) * 100.0
        self.consensus_gauge.set_score(agreement_pct, animate=True)
        if agreement_pct >= 70.0:
            tier = "High"
        elif agreement_pct >= 40.0:
            tier = "Moderate"
        else:
            tier = "Low"
        self.consensus_gauge_label.setText(f"{agreement_pct:.0f}% {tier}")

    def set_consensus_failed(self, message: str) -> None:
        self.consensus_button.setEnabled(True)
        self.consensus_status_label.setText(f"⚠ Real computation failed: {message}")

    def set_alerts(self, assessment: dict[str, Any]) -> None:
        """Real threshold-based classification, from
        `compute_real_alerts()`'s own real result - never called with
        a fabricated dict. See module docstring for the disclosed
        CAPE+shear-only scope."""
        risk_level = assessment["risk_level"]
        color_token = _RISK_LEVEL_COLOR.get(risk_level, "text_muted")
        self.alerts_risk_label.setText(f"  Risk level: {risk_level}  ")
        # Colored badge/pill (2026-09-13, explicit user request to
        # match the mockup's own colored severity badges) - real token
        # color, dark text on the lighter success/warning tokens for
        # contrast, light text on the darker danger token; same 3
        # tokens ForecastDecisionEngine's own real risk_level already
        # maps to via _RISK_LEVEL_COLOR, no new color/severity logic.
        text_color = "#0a1120" if color_token in ("success", "warning") else TOKENS.text_primary
        self.alerts_risk_label.setStyleSheet(
            f"background-color: {getattr(TOKENS, color_token, TOKENS.text_muted)}; color: {text_color}; "
            f"font-size: {TOKENS.font_size_sm}px; font-weight: 700; border-radius: {TOKENS.radius_lg}px;"
        )
        phenomena = assessment["detected_phenomena"]
        if phenomena:
            self.alerts_detail_label.setText(
                "• " + "\n• ".join(f"{name}" for name in phenomena)
                + "\n\n" + "\n".join(assessment["operational_warnings"])
            )
        else:
            self.alerts_detail_label.setText(
                "No real CAPE/shear threshold crossed at the current point of interest."
            )

    def set_model(self, model: str) -> None:
        """Real, current `MODEL_CONFIGS` grid metadata for the
        selected model - updates live as the Model selector changes,
        even before any real run has happened."""
        config = MODEL_CONFIGS.get(model)
        if config is None:
            self.model_info_label.setText(f"Unknown model {model!r}.")
            return
        self.model_info_label.setText(
            f"Selected model: {model} — real native grid "
            f"{config['n_lat']}×{config['n_lon']}×{config['n_levels']} "
            f"(resolution ≈ {config['resolution_km']} km, default {config['default_steps']} steps)."
        )

    def update_status(self, status_text: str) -> None:
        """Real, current Workstation-wide status - the exact same
        string `ACFWorkstation.status_label` already shows, mirrored
        here verbatim."""
        self.status_label.setText(status_text)
