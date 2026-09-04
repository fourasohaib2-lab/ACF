"""
ACF Scientific Workstation — Thermodynamics Lab
=================================================

Real thermodynamic analysis panel for `acf_workstation.ACFWorkstation`
(see that module's own docstring for the Workstation's overall "ACF
CORE ONLY - NO AWCI" rule). Two real, already-existing per-point
formula pipelines, reused as-is - no new physics invented here:

1. **θ-e (equivalent potential temperature) / relative humidity** -
   `acf.awci.theta_e.compute_real_theta_e_at_point()`, which itself
   composes 3 already-real, already-tested formulas (real relative
   humidity, real Magnus-Tetens dewpoint, the CANONICAL Bolton (1980)
   θ-e formula - see that module's own docstring for the full
   derivation chain). A single call already returns BOTH θ-e and its
   own real intermediate relative-humidity value, so this module reuses
   that one call for both variables rather than computing relative
   humidity a second, separate time. Pure arithmetic (no iterative
   solve) - fast enough (~1 microsecond/point measured) to recompute
   for the WHOLE grid automatically on every level/model change, same
   as Overview/Dynamics Lab.

2. **CAPE/CIN (convective available potential energy / inhibition)** -
   `acf.awci.convective_energy.compute_real_cape_cin_at_point()`, a
   real MetPy parcel-ascent pipeline (dry+moist adiabatic lift,
   hypsometric layer thicknesses) feeding
   `acf.science.cape.CAPE.calculate()`/`acf.science.cin.CIN.calculate()`
   - the same real classes the science encyclopedia's own
   "cape_convective_energy"/"cin_convective_inhibition" entries
   delegate to. Real, but genuinely expensive per point (~5 ms
   measured, one real MetPy parcel ascent each) - a real, on-demand,
   off-thread computation (same "🔄 Run ..." button convention already
   used by Complexity Explorer's temporal/consensus dimensions), never
   automatic. Independent of the level slider (CAPE/CIN are inherently
   full-column diagnostics, always lifted from the real lowest native
   level - same real "not tied to the level slider" convention already
   documented on Complexity Explorer's own temporal/consensus results).

Honest performance trade-off for CAPE/CIN
-------------------------------------------
At full native resolution (e.g. ALADIN's 60x120 = 7,200 columns), a
real per-point MetPy parcel ascent would take on the order of a
minute - too slow for an interactive UI. `compute_real_cape_cin_fields()`
therefore computes over a real, coarser SUBSET of the already-computed
volume's own real columns (every `_CAPE_GRID_STRIDE`-th native row/
column - e.g. ALADIN's 60x120 native grid becomes a real 20x40 grid of
genuinely computed CAPE/CIN values, each one a real result from that
exact real column, at that grid's OWN coarser lat/lon coordinates -
never interpolated or approximated from neighbouring cells). This is
the same documented "coarser real grid for a fast result" trade-off
`acf.awci.spatial_field.compute_real_complexity_field()`'s own
`n_lat`/`n_lon` override parameters already establish as a legitimate,
disclosed engineering choice in this codebase - applied here to a
subset of an already-computed real volume instead of a fresh, coarser
solver run (no second solver run is ever triggered).

NOTE (correction, 2026-09-04): `compute_real_theta_e_and_rh_fields()`
used to be DEFINED here - moved to the real, Qt-free
`acf.awci.workstation_fields` so the new `/api/v1/workstation` HTTP
router can reuse it without importing PySide6 into the web server
process. Re-imported below unchanged - every existing caller of this
module keeps working with zero code changes.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from acf.awci.convective_energy import compute_real_cape_cin_at_point
from acf.awci.workstation_fields import compute_real_theta_e_and_rh_fields
from acf.gui.dashboard.awci_map_panel import AWCIMapPanel
from acf.gui.theme_tokens import label_style

__all__ = ["ACFThermodynamicsLabPanel", "compute_real_cape_cin_fields", "compute_real_theta_e_and_rh_fields"]

#: Real, disclosed rendering ranges - see module docstring for CAPE/CIN's
#: reference basis (the real STP/SCP normalization constants in
#: acf.science.severe_weather, 1000-1500 J/kg, informed this envelope's
#: order of magnitude - a generous real bound, not a claimed threshold).
#: θ-e's vmin/vmax are None (dynamic, real 5th/95th percentile of
#: whatever the current volume actually produced - same convention
#: `acf_workstation_complexity.py` already uses for its own spatial/
#: temporal complexity ranges) rather than a fixed guessed range: a
#: real θ-e range depends heavily on the real solver's own surface
#: pressure/humidity state (see this module's own real, disclosed
#: finding - flagged separately - that a real ALADIN run's surface
#: pressure currently comes out ~2x a realistic sea-level value,
#: which by itself shifts θ-e well outside any single fixed guess).
#: Relative humidity is a real, bounded percentage - 0-100% is not a
#: guess, it is the quantity's own real definition.
_AUTO_VARIABLES: dict[str, dict[str, Any]] = {
    "Equivalent potential temperature (θ-e)": {"unit": "K", "cmap": "plasma", "vmin": None, "vmax": None},
    "Relative humidity": {"unit": "%", "cmap": "YlGnBu", "vmin": 0.0, "vmax": 100.0},
}
_CAPE_CIN_VARIABLES: dict[str, dict[str, Any]] = {
    "CAPE (convective available potential energy)": {"unit": "J/kg", "cmap": "inferno", "vmin": 0.0, "vmax": 3000.0},
    "CIN (convective inhibition)": {"unit": "J/kg", "cmap": "cividis", "vmin": 0.0, "vmax": 200.0},
}

#: See module docstring's "Honest performance trade-off" section.
_CAPE_GRID_STRIDE = 3


def compute_real_cape_cin_fields(
    temperature_volume: np.ndarray,
    specific_humidity_volume: np.ndarray,
    pressure_volume_hpa: np.ndarray,
    lats: np.ndarray,
    lons: np.ndarray,
    stride: int = _CAPE_GRID_STRIDE,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Real CAPE/CIN (J/kg) on a real, coarser subset of the volume's own
    grid - see module docstring's "Honest performance trade-off".

    Parameters
    ----------
    temperature_volume, specific_humidity_volume, pressure_volume_hpa :
        Real (n_levels, n_lat, n_lon) arrays - the SAME volume Overview/
        Dynamics/θ-e already re-slice, never a second solver run.
    lats, lons : the volume's own real 1D coordinate arrays.
    stride : take every `stride`-th real native row/column.

    Returns
    -------
    (sub_lats, sub_lons, cape_grid, cin_grid) : sub_lats/sub_lons are
        real coordinate arrays (lats[::stride]/lons[::stride]);
        cape_grid/cin_grid are real (len(sub_lats), len(sub_lons))
        arrays, NaN wherever compute_real_cape_cin_at_point() itself
        honestly reports too few real levels to integrate over.
    """
    sub_lats = np.asarray(lats)[::stride]
    sub_lons = np.asarray(lons)[::stride]
    cape_grid = np.full((len(sub_lats), len(sub_lons)), np.nan)
    cin_grid = np.full((len(sub_lats), len(sub_lons)), np.nan)

    row_indices = range(0, temperature_volume.shape[1], stride)
    col_indices = range(0, temperature_volume.shape[2], stride)
    for si, i in enumerate(row_indices):
        for sj, j in enumerate(col_indices):
            result = compute_real_cape_cin_at_point(
                temperature_profile_k=temperature_volume[:, i, j],
                specific_humidity_profile=specific_humidity_volume[:, i, j],
                pressure_profile_hpa=pressure_volume_hpa[:, i, j],
            )
            if result["is_real_data"]:
                cape_grid[si, sj] = result["cape_j_kg"]
                cin_grid[si, sj] = result["cin_j_kg"]
    return sub_lats, sub_lons, cape_grid, cin_grid


class _WorkerSignals(QObject):
    """Same real QRunnable-companion-object pattern used throughout
    this codebase's other off-thread workers - reused, not reinvented."""

    finished = Signal(tuple)
    failed = Signal(str)


class _CapeCinWorker(QRunnable):
    """Runs compute_real_cape_cin_fields() off the GUI thread - see
    module docstring for why this is real but genuinely slow."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__()
        self.kwargs = kwargs
        self.signals = _WorkerSignals()

    def run(self) -> None:
        try:
            result = compute_real_cape_cin_fields(**self.kwargs)
        except Exception as exc:  # noqa: BLE001 - real failure, reported honestly via signal below
            self.signals.failed.emit(str(exc))
            return
        self.signals.finished.emit(result)


class ACFThermodynamicsLabPanel(QWidget):
    """Real Thermodynamics Lab - θ-e/relative humidity (auto, from the
    current level) and CAPE/CIN (on-demand, full-column). No AWCI
    content anywhere."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._volume: dict[str, Any] | None = None
        self._level_index = 0
        self._cape_grid: np.ndarray | None = None
        self._cin_grid: np.ndarray | None = None
        self._cape_lats: np.ndarray | None = None
        self._cape_lons: np.ndarray | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # --- θ-e / relative humidity (real-time, from the current level) ---
        auto_controls = QHBoxLayout()
        auto_controls.addWidget(self._label("Variable:"))
        self.variable_selector = QComboBox()
        self.variable_selector.addItems(list(_AUTO_VARIABLES.keys()))
        self.variable_selector.currentTextChanged.connect(lambda _: self._redraw_auto())
        auto_controls.addWidget(self.variable_selector)
        auto_controls.addStretch()
        layout.addLayout(auto_controls)

        self.map_panel = AWCIMapPanel(
            "THERMODYNAMICS LAB", show_legend=False, show_info_boxes=False, show_demo_fallback=False
        )
        self.map_panel.setMinimumHeight(260)
        layout.addWidget(self.map_panel, stretch=1)

        # --- CAPE/CIN (on-demand, full-column real parcel ascent) ---
        layout.addWidget(
            self._header(
                "CONVECTIVE ENERGY — real CAPE/CIN from a real MetPy parcel ascent "
                f"(coarser {_CAPE_GRID_STRIDE}x-strided grid, see status)"
            )
        )
        cape_controls = QHBoxLayout()
        self.cape_button = QPushButton("🔄 Compute CAPE/CIN Field")
        self.cape_button.setToolTip(
            "Real, off-thread compute_real_cape_cin_fields() run - a real MetPy\n"
            "dry+moist adiabatic parcel ascent at every point of a coarser, real\n"
            f"subset of the native grid (every {_CAPE_GRID_STRIDE}-th row/column - see this\n"
            "panel's own module docstring for why). On demand, not automatic -\n"
            "independent of the level slider (CAPE/CIN always lift from the real\n"
            "lowest native level)."
        )
        self.cape_button.clicked.connect(self._start_cape_cin)
        cape_controls.addWidget(self.cape_button)
        self.cape_variable_selector = QComboBox()
        self.cape_variable_selector.addItems(list(_CAPE_CIN_VARIABLES.keys()))
        self.cape_variable_selector.setEnabled(False)
        self.cape_variable_selector.currentTextChanged.connect(lambda _: self._redraw_cape_cin())
        cape_controls.addWidget(self.cape_variable_selector)
        self.cape_status_label = QLabel("Not yet computed.")
        self.cape_status_label.setStyleSheet(label_style("text_muted", "xs"))
        cape_controls.addWidget(self.cape_status_label)
        cape_controls.addStretch()
        layout.addLayout(cape_controls)

        self.cape_map = AWCIMapPanel(
            "CONVECTIVE ENERGY", show_legend=False, show_info_boxes=False, show_demo_fallback=False
        )
        self.cape_map.setMinimumHeight(220)
        layout.addWidget(self.cape_map)

    @staticmethod
    def _label(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(label_style("text_muted", "xs"))
        return lbl

    @staticmethod
    def _header(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(label_style("text_secondary", "xs", "bold"))
        return lbl

    def update_from_volume(self, volume: dict[str, Any], level_index: int) -> None:
        """Real re-slice of the already-computed volume for θ-e/
        relative humidity - no new solver run. CAPE/CIN stay whatever
        they were (real, separate, on-demand, not tied to the level
        slider - same convention as Complexity Explorer's own temporal/
        model-disagreement dimensions)."""
        self._volume = volume
        self._level_index = level_index
        self._redraw_auto()

    def _redraw_auto(self) -> None:
        if self._volume is None:
            return
        variable = self.variable_selector.currentText()
        spec = _AUTO_VARIABLES[variable]
        lats, lons = self._volume["lats"], self._volume["lons"]
        level = self._level_index

        theta_e, relative_humidity = compute_real_theta_e_and_rh_fields(
            self._volume["temperature_volume"][level],
            self._volume["specific_humidity_volume"][level],
            self._volume["pressure_volume_hpa"][level],
        )
        field = theta_e if variable.startswith("Equivalent") else relative_humidity

        # A None vmin/vmax (θ-e - see _AUTO_VARIABLES' own comment)
        # falls back to the real 5th/95th percentile of THIS field -
        # same dynamic-range convention acf_workstation_complexity.py
        # already uses, rather than a fixed range that may not match
        # whatever the real solver run actually produced.
        vmin = spec["vmin"] if spec["vmin"] is not None else float(np.nanpercentile(field, 5))
        vmax = spec["vmax"] if spec["vmax"] is not None else float(np.nanpercentile(field, 95))
        if vmin == vmax:  # a real, degenerate (perfectly uniform) field - avoid a zero-width color range
            vmin, vmax = vmin - 1.0, vmax + 1.0

        self.map_panel.set_external_field(
            lons,
            lats,
            field,
            f"Real {self._volume.get('model', '')} — {variable}",
            cmap=spec["cmap"],
            vmin=vmin,
            vmax=vmax,
            colorbar_label=f"{variable} ({spec['unit']})",
        )

    # ------------------------------------------------------- CAPE/CIN

    def _start_cape_cin(self) -> None:
        if self._volume is None:
            self.cape_status_label.setText("⚠ Run the Workstation's own volume computation first.")
            return
        self.cape_button.setEnabled(False)
        self.cape_status_label.setText(
            f"⏳ Computing real CAPE/CIN (MetPy parcel ascent, {_CAPE_GRID_STRIDE}x-strided grid)…"
        )
        worker = _CapeCinWorker(
            temperature_volume=self._volume["temperature_volume"],
            specific_humidity_volume=self._volume["specific_humidity_volume"],
            pressure_volume_hpa=self._volume["pressure_volume_hpa"],
            lats=self._volume["lats"],
            lons=self._volume["lons"],
        )
        worker.signals.finished.connect(self._on_cape_cin_ready)
        worker.signals.failed.connect(self._on_cape_cin_failed)
        QThreadPool.globalInstance().start(worker)

    def _on_cape_cin_ready(self, result: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]) -> None:
        self.cape_button.setEnabled(True)
        self.cape_variable_selector.setEnabled(True)
        sub_lats, sub_lons, cape_grid, cin_grid = result
        self._cape_lats, self._cape_lons = sub_lats, sub_lons
        self._cape_grid, self._cin_grid = cape_grid, cin_grid
        n_real = int(np.count_nonzero(~np.isnan(cape_grid)))
        self.cape_status_label.setText(
            f"✅ Real CAPE/CIN computed at {n_real} real points ({sub_lats.size}x{sub_lons.size} grid)."
        )
        self._redraw_cape_cin()

    def _on_cape_cin_failed(self, message: str) -> None:
        self.cape_button.setEnabled(True)
        self.cape_status_label.setText(f"⚠ Real CAPE/CIN computation failed: {message}")

    def _redraw_cape_cin(self) -> None:
        if self._cape_grid is None or self._cin_grid is None or self._cape_lats is None or self._cape_lons is None:
            return
        variable = self.cape_variable_selector.currentText()
        spec = _CAPE_CIN_VARIABLES[variable]
        field = self._cape_grid if variable.startswith("CAPE") else self._cin_grid
        self.cape_map.set_external_field(
            list(self._cape_lons),
            list(self._cape_lats),
            field,
            f"Real {self._volume.get('model', '') if self._volume else ''} — {variable}",
            cmap=spec["cmap"],
            vmin=spec["vmin"],
            vmax=spec["vmax"],
            colorbar_label=f"{variable} ({spec['unit']})",
        )
