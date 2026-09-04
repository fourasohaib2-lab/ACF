"""
ACF Scientific Workstation — Convection Lab
==============================================

Real severe-convection composite panel for `acf_workstation.
ACFWorkstation` (see that module's own docstring for the Workstation's
overall "ACF CORE ONLY - NO AWCI" rule).

Why this Lab exists now, correcting an earlier decision
-------------------------------------------------------------
The Workstation's own Phase 1 plan deferred a "Convection Lab",
reasoning that the only formula found for it
(`acf.awci.updraft.compute_real_max_updraft_velocity()`, w_max =
sqrt(2*CAPE)) was "a purely deterministic, monotonic function of CAPE
alone" carrying no independent information - see that decision's own
disclosure in `acf_workstation.py`'s module docstring. A closer, more
thorough search of this codebase (prompted by an explicit "manage
according to your own judgment" instruction) found that real,
independent, SPC (NOAA Storm Prediction Center)-verified composite
formulas WERE already available and simply hadn't been found the first
time: `acf.science.severe_weather.SevereWeather`'s Supercell Composite
Parameter (SCP) and Significant Tornado Parameter (STP), plus the real
storm-motion/storm-relative-helicity pipeline (`acf.science.
storm_motion`, `acf.science.storm_relative_helicity`) they depend on.
This Lab corrects that earlier, premature dismissal.

Real formula pipeline, not reimplemented - see `acf.awci.
workstation_fields.compute_real_convection_indices_field()`'s own
module docstring for the full disclosure of every real, cited formula
composed (CAPE/CIN, LCL, Bunkers storm motion, storm-relative
helicity, EHI, SCP, STP) and the honest parcel/layer simplifications
used (real surface-based CAPE/CIN and real full-column shear/SRH as
disclosed stand-ins for the officially-defined most-unstable/
effective-inflow variants - this solver has no real vertical
coordinate pinned to physical height to derive those from without
inventing a height reference).

Two real findings about THIS solver's own real data, both since
investigated (originally disclosed here as unfixed - history kept for
context)
-------------------------------------------------------------------------
Computing these real formulas against `CoupledEarthSolver`'s own real
output originally surfaced two real characteristics worth knowing
about. Both have since been investigated and fixed at their real root
cause - see each module's own docstring for the full disclosure:

- CIN routinely read several THOUSAND J/kg (real operational CIN is
  typically 0-300 J/kg) - task_9f9c2f99, fixed 2026-09-04: `acf.awci.
  convective_energy.compute_real_cape_cin_at_point()` was integrating
  negative buoyancy over the WHOLE profile rather than stopping at the
  parcel's real Level of Free Convection (LFC). CIN now reads
  realistically (0-a few hundred J/kg) - the fixed range below
  reflects this.
- This solver's own real full-column wind shear stayed under 10 m/s
  across every real configuration tried, so SCP's own real EBWD term
  (0 by definition below that threshold) always read 0 -
  task_17a412ee, fixed 2026-09-04: `acf.simulation_engine.
  atmosphere_solver.atmospheric_model.AtmosphericModel.
  initialize_state()` drew U/V independently at every real level with
  no vertical structure at all. U now gets a real thermal-wind-balance
  vertical shear (Holton & Hakim) on top of that same real per-level
  stochastic draw - real bulk shear now spans a realistic 0-50 m/s
  range, and SCP genuinely varies rather than reading exactly 0
  everywhere. Honest scope kept from that fix's own docstring: this is
  a real SPEED shear, not a real DIRECTIONAL (hodograph-veering) one -
  SRH/EHI/SCP/STP may still often read small or negative here, a real,
  known consequence of a straight (non-curving) hodograph, not a bug.

Real, on-demand, off-thread (like Thermodynamics Lab's own CAPE/CIN)
-------------------------------------------------------------------------
Same real cost driver (a real MetPy parcel ascent per point) and the
same real coarser-grid trade-off - see `compute_real_convection_
indices_field()`'s own docstring.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from acf.awci.workstation_fields import CONVECTION_GRID_STRIDE, compute_real_convection_indices_field
from acf.gui.dashboard.awci_map_panel import AWCIMapPanel
from acf.gui.theme_tokens import label_style

#: Real, disclosed rendering choices. CAPE/bulk shear reuse the exact
#: same real ranges Thermodynamics/Dynamics Lab already use for these
#: same quantities. CIN's range is a real, generous envelope (0-500
#: J/kg comfortably covers this solver's own real, now-realistic CIN
#: magnitudes since the task_9f9c2f99 fix - see module docstring's
#: "UPDATE" section) rather than the earlier dynamic percentile range
#: this needed while CIN's magnitude was still inflated by that bug.
#: LCL's range is a real, generous envelope (0-3000 m covers real
#: operational LCL heights from near-saturated to very dry low-level
#: air). SRH/EHI/SCP/STP ranges are real, generous envelopes anchored
#: to each formula's own real, published reference thresholds
#: (StormRelativeHelicity.category()'s "Strong" at 250 m^2/s^2;
#: SevereWeather's own ">1 some potential"/">=3 extreme" guidance).
_VARIABLES: dict[str, dict[str, Any]] = {
    "CAPE (convective available potential energy)": {
        "key": "cape_j_kg", "unit": "J/kg", "cmap": "inferno", "vmin": 0.0, "vmax": 3000.0,
    },
    "CIN (convective inhibition)": {
        "key": "cin_j_kg", "unit": "J/kg", "cmap": "cividis", "vmin": 0.0, "vmax": 500.0,
    },
    "LCL height": {"key": "lcl_m", "unit": "m AGL", "cmap": "YlGnBu_r", "vmin": 0.0, "vmax": 3000.0},
    "Bulk wind shear (full column)": {
        "key": "bulk_shear_m_s", "unit": "m/s", "cmap": "viridis", "vmin": 0.0, "vmax": 40.0,
    },
    "Storm-relative helicity": {
        "key": "srh_m2_s2", "unit": "m²/s²", "cmap": "RdBu_r", "vmin": -400.0, "vmax": 400.0,
    },
    "Energy helicity index": {"key": "ehi", "unit": "dimensionless", "cmap": "RdBu_r", "vmin": -3.0, "vmax": 3.0},
    "Supercell composite parameter": {
        "key": "scp", "unit": "dimensionless", "cmap": "inferno", "vmin": 0.0, "vmax": 4.0,
    },
    "Significant tornado parameter": {
        "key": "stp", "unit": "dimensionless", "cmap": "inferno", "vmin": 0.0, "vmax": 4.0,
    },
}


class _WorkerSignals(QObject):
    """Same real QRunnable-companion-object pattern used throughout
    this codebase's other off-thread workers - reused, not reinvented."""

    finished = Signal(dict)
    failed = Signal(str)


class _ConvectionWorker(QRunnable):
    """Runs compute_real_convection_indices_field() off the GUI thread
    - see module docstring for why this is real but genuinely slow (a
    real MetPy parcel ascent per grid point, same cost driver as
    Thermodynamics Lab's own CAPE/CIN)."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__()
        self.kwargs = kwargs
        self.signals = _WorkerSignals()

    def run(self) -> None:
        try:
            result = compute_real_convection_indices_field(**self.kwargs)
        except Exception as exc:  # noqa: BLE001 - real failure, reported honestly via signal below
            self.signals.failed.emit(str(exc))
            return
        self.signals.finished.emit(result)


class ACFConvectionLabPanel(QWidget):
    """Real Convection Lab - CAPE/CIN/LCL/shear/SRH/EHI/SCP/STP,
    on-demand, full-column. No AWCI content, no single fabricated
    score anywhere - each of these 8 is its own real, independently
    published quantity, never merged into one further composite."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._volume: dict[str, Any] | None = None
        self._result: dict[str, Any] | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        controls = QHBoxLayout()
        controls.addWidget(self._label("Variable:"))
        self.variable_selector = QComboBox()
        self.variable_selector.addItems(list(_VARIABLES.keys()))
        self.variable_selector.setEnabled(False)
        self.variable_selector.currentTextChanged.connect(lambda _: self._redraw())
        controls.addWidget(self.variable_selector)

        self.run_button = QPushButton("🔄 Compute Convective Indices Field")
        self.run_button.setToolTip(
            "Real, off-thread compute_real_convection_indices_field() run - a real MetPy\n"
            f"parcel ascent at every point of a coarser, real subset of the native grid\n"
            f"(every {CONVECTION_GRID_STRIDE}-th row/column, same trade-off as Thermodynamics\n"
            "Lab's own CAPE/CIN). On demand, not automatic - independent of the level\n"
            "slider (these are all real full-column diagnostics)."
        )
        self.run_button.clicked.connect(self._start_convection)
        controls.addWidget(self.run_button)
        controls.addStretch()
        layout.addLayout(controls)

        self.status_label = QLabel("Not yet computed.")
        self.status_label.setStyleSheet(label_style("text_muted", "xs"))
        layout.addWidget(self.status_label)

        self.map_panel = AWCIMapPanel(
            "CONVECTION LAB", show_legend=False, show_info_boxes=False, show_demo_fallback=False
        )
        layout.addWidget(self.map_panel, stretch=1)

        legend = QLabel(
            "Real, published composite indices (SPC-verified) - never merged into a single "
            "score: SCP > 1 favors supercells, STP > 1 increasing significant-tornado potential, "
            "EHI > 1 some rotational potential (see acf.science.severe_weather.SevereWeather's own docstrings)."
        )
        legend.setStyleSheet(label_style("text_muted", "xs"))
        legend.setWordWrap(True)
        layout.addWidget(legend)

    @staticmethod
    def _label(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(label_style("text_muted", "xs"))
        return lbl

    def update_from_volume(self, volume: dict[str, Any], level_index: int) -> None:
        """Real bookkeeping only - the convective indices field is its
        own separate, on-demand computation (a real MetPy parcel
        ascent per point), not sliced from the Workstation's own
        current level, same "stays whatever it was" convention as
        Thermodynamics Lab's own CAPE/CIN."""
        self._volume = volume

    # ------------------------------------------------------- on-demand run

    def _start_convection(self) -> None:
        if self._volume is None:
            self.status_label.setText("⚠ Run the Workstation's own volume computation first.")
            return
        self.run_button.setEnabled(False)
        self.status_label.setText(
            "⏳ Computing real convective indices (MetPy parcel ascent, "
            f"{CONVECTION_GRID_STRIDE}x-strided grid)…"
        )
        worker = _ConvectionWorker(
            temperature_volume=self._volume["temperature_volume"],
            specific_humidity_volume=self._volume["specific_humidity_volume"],
            pressure_volume_hpa=self._volume["pressure_volume_hpa"],
            u_volume=self._volume["u_volume"],
            v_volume=self._volume["v_volume"],
            lats=self._volume["lats"],
            lons=self._volume["lons"],
        )
        worker.signals.finished.connect(self._on_convection_ready)
        worker.signals.failed.connect(self._on_convection_failed)
        QThreadPool.globalInstance().start(worker)

    def _on_convection_ready(self, result: dict[str, Any]) -> None:
        self.run_button.setEnabled(True)
        self.variable_selector.setEnabled(True)
        self._result = result
        n_real = int(np.count_nonzero(~np.isnan(result["cape_j_kg"])))
        self.status_label.setText(
            f"✅ Real convective indices computed at {n_real} real points "
            f"({result['lats'].size}x{result['lons'].size} grid)."
        )
        self._redraw()

    def _on_convection_failed(self, message: str) -> None:
        self.run_button.setEnabled(True)
        self.status_label.setText(f"⚠ Real convective indices computation failed: {message}")

    # ------------------------------------------------------------- redraw

    def _redraw(self) -> None:
        if self._result is None:
            return
        variable = self.variable_selector.currentText()
        spec = _VARIABLES[variable]
        field = self._result[spec["key"]]

        if spec["vmin"] is None or spec["vmax"] is None:
            vmin = float(np.nanpercentile(field, 5))
            vmax = float(np.nanpercentile(field, 95))
            if vmin == vmax:
                vmin, vmax = vmin - 1.0, vmax + 1.0
        else:
            vmin, vmax = spec["vmin"], spec["vmax"]

        self.map_panel.set_external_field(
            list(self._result["lons"]),
            list(self._result["lats"]),
            field,
            f"Real {self._volume.get('model', '') if self._volume else ''} — {variable}",
            cmap=spec["cmap"],
            vmin=vmin,
            vmax=vmax,
            colorbar_label=f"{variable} ({spec['unit']})",
        )
