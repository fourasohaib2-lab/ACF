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

Two deliberate, disclosed departures from the mockup's own numbers -
this project's own master spec (§21/§67) explicitly and repeatedly
forbids exactly the kind of single fabricated composite/normalized
score the mockup's raw "0.72"/"78% High" style implies:

1. The mockup's "Complexity Index" card (a single 0-1 composite) is
   replaced here with **Spatial Complexity** (K/100km) - one of
   Complexity Explorer's own 3 already-real, already-disclosed,
   never-combined complexity dimensions
   (`acf_workstation_complexity.compute_real_spatial_complexity()`),
   sampled at this page's own point of interest. "Instability" and
   "Shear" ARE the real CAPE (J/kg) and bulk wind shear (m/s) already
   computed by Stability Indices' own `compute_real_stability_indices_
   at_point()` - shown with their real physical units, not squeezed
   into a fabricated unitless 0-1 range. "Moisture" is the real
   relative humidity (%) `compute_real_theta_e_at_point()` already
   derives - the same real function the Map Inspector and
   Microphysics Lab already use.
2. The mockup's circular "Agreement Level: 78% High" gauge implies a
   normalized confidence percentage that does not exist anywhere in
   this codebase's real model-consensus math - `ModelConsensusEngine.
   compute_real_multi_model_disagreement()` returns a real spread/mean
   in the compared field's own physical unit (K for temperature), not
   a percentage; inventing a 0-100% mapping from it (with no real,
   disclosed reference scale to normalize against) would itself be a
   fabricated composite score. This page instead shows the real
   per-model values and the real spread, in real units - the exact
   same real numbers Complexity Explorer's own "Model Disagreement"
   dimension already surfaces, reused here (same engine, a separate,
   independently-triggered real computation) rather than reinvented.
   Only the real 3 MODEL_CONFIGS models this codebase actually has
   (AROME/ALADIN/ARPEGE) are compared - the mockup's own 4th "WRF" row
   has no real backing anywhere in this codebase, so it is not shown.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np
from PySide6.QtWidgets import QGridLayout, QGroupBox, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from acf.awci.theta_e import compute_real_theta_e_at_point
from acf.forecast.engine import MODEL_CONFIGS
from acf.gui.dashboard.acf_workstation_complexity import compute_real_spatial_complexity
from acf.gui.dashboard.acf_workstation_stability_indices import compute_real_stability_indices_at_point
from acf.gui.theme_tokens import label_style

#: Real, ordered (label, dict-key, unit, decimal digits) for the Key
#: Metrics row - see compute_real_key_metrics_at_point()'s own
#: docstring for what each real value is.
_KEY_METRICS: tuple[tuple[str, str, str, int], ...] = (
    ("Spatial Complexity", "spatial_complexity_k_per_100km", "K/100km", 2),
    ("Instability (CAPE)", "cape_j_kg", "J/kg", 0),
    ("Moisture (RH)", "relative_humidity_pct", "%", 1),
    ("Shear", "bulk_wind_shear_ms", "m/s", 2),
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


class ACFOverviewLandingPanel(QWidget):
    """Real Workstation landing page - status + quick navigation, no
    map, no composite score, nothing fabricated."""

    def __init__(
        self,
        navigate_to: Callable[[str], None],
        module_names: list[str],
        compute_consensus: Callable[[], None] | None = None,
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

        # --- Key Metrics (Phase 44, 2026-09-12) - real per-point values,
        # see compute_real_key_metrics_at_point()'s own docstring for
        # exactly what backs each one and why this differs from the new
        # reference mockup's own fabricated-looking 0-1 numbers.
        metrics_group = QGroupBox("Key Metrics")
        metrics_grid = QGridLayout(metrics_group)
        self._metric_value_labels: dict[str, QLabel] = {}
        self._metric_point_label = QLabel("No real point of interest yet - click a map, or run a real analysis first.")
        self._metric_point_label.setWordWrap(True)
        self._metric_point_label.setStyleSheet(label_style("text_muted", "xs"))
        metrics_grid.addWidget(self._metric_point_label, 0, 0, 1, 2)
        for i, (label, key, unit, _digits) in enumerate(_KEY_METRICS):
            row = i // 2 + 1
            col = (i % 2) * 2
            name_label = QLabel(label)
            name_label.setStyleSheet(label_style("text_secondary", "xs", "bold"))
            value_label = QLabel("—")
            value_label.setStyleSheet(label_style("text_primary", "lg", "bold"))
            metrics_grid.addWidget(name_label, row, col)
            metrics_grid.addWidget(value_label, row, col + 1)
            self._metric_value_labels[key] = value_label
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
        self.consensus_models_label = QLabel()
        self.consensus_models_label.setWordWrap(True)
        self.consensus_models_label.setStyleSheet(label_style("text_secondary", "sm"))
        consensus_layout.addWidget(self.consensus_models_label)
        layout.addWidget(consensus_group)

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
        dict."""
        self._metric_point_label.setText(
            f"Point of interest: {metrics['lat']:.2f}°N, {metrics['lon']:.2f}°E (real surface level)."
        )
        for label, key, unit, digits in _KEY_METRICS:
            value = metrics.get(key)
            widget = self._metric_value_labels[key]
            if value is None:
                widget.setText("N/A")
                widget.setStyleSheet(label_style("text_muted", "lg", "bold"))
            else:
                widget.setText(f"{value:.{digits}f} {unit}")
                widget.setStyleSheet(label_style("text_primary", "lg", "bold"))

    def set_consensus_pending(self) -> None:
        self.consensus_button.setEnabled(False)
        self.consensus_status_label.setText("⏳ Computing (one real solver run per model)…")

    def set_consensus_result(self, result: dict[str, Any]) -> None:
        """Real per-model values + real spread, from `ModelConsensusEngine.
        compute_real_multi_model_disagreement()`'s own real result -
        see module docstring for why no fabricated percentage is shown."""
        self.consensus_button.setEnabled(True)
        variable_label = "temperature" if result["field"] == "T" else result["field"]
        self.consensus_status_label.setText(
            f"✅ Real spread ({variable_label}): {result['disagreement_spread']:.3f} K "
            f"(mean {result['disagreement_mean']:.2f} K)."
        )
        lines = [f"{model}: {value:.2f} K" for model, value in result["per_model_value"].items()]
        self.consensus_models_label.setText(" · ".join(lines))

    def set_consensus_failed(self, message: str) -> None:
        self.consensus_button.setEnabled(True)
        self.consensus_status_label.setText(f"⚠ Real computation failed: {message}")

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
